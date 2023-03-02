from django.test import Client
from core.tests.utils import asserts, create_user, jget, login, TaskTestCase, logout
from core.models import Repository, Scan, Vulnerability
from datetime import datetime, timedelta
import uuid
from django.utils.timezone import make_aware
from unittest import mock

client = Client()


@mock.patch('celery.backends.base.Backend._ensure_not_eager', mock.MagicMock(return_value=None))
class ScanViewTestCase(TaskTestCase):

    def test_user_can_access_owned_scan(self):
        user = create_user("user", "user", "user")
        user2 = create_user("user2", "user2", "user2")
        repo = Repository(name="Repo1", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        repo2 = Repository(name="Repo2", url='https://github.com/zenscanner/public-testing', owner=user2)
        repo2.save()
        Scan(repository=repo).save()
        scan = Scan(repository=repo2)
        scan.save()
        scan.created_at = make_aware(datetime.today() - timedelta(days=5))
        scan.save()
        login(client, "user2", "user2")
        res = jget(client, "/api/scans").json()
        self.assertEqual(res['count'], 1)
        self.assertEqual(res['items'][0]['repository']['name'], repo2.name)
        asserts(self, jget(client, "/api/scans/" + str(uuid.uuid4())), status=404)
        res = jget(client, "/api/scans/" + str(scan.uuid)).json()
        self.assertEqual(res['repository']['name'], "Repo2")
        self.assertEqual(res['uuid'], str(scan.uuid))
        Scan(repository=repo2).save()
        asserts(self,
                jget(client, "/api/scans?days=1"),
                status=200,
                json_contains={"count": 1},
                )
        asserts(self,
                jget(client, "/api/scans?days=-1"),
                status=422,
                )
        asserts(self,
                jget(client, "/api/scans?days=a"),
                status=422,
                )
        asserts(self,
                jget(client, "/api/scans?days=7"),
                status=200,
                json_contains={"count": 2},
                )
        asserts(self,
                jget(client, "/api/scans?days=7&status=SUCCESS"),
                status=200,
                json_contains={"count": 0},
                )
        asserts(self,
                jget(client, "/api/scans?days=7&status=PENDING&status=SUCCESS"),
                status=200,
                json_contains={"count": 2},
                )

    def test_user_can_see_new_vulnerability_count(self):
        user = create_user("user", "user", "user")
        r = Repository(name="repo1", url="https://repo1", owner=user)
        r.save()
        s = Scan(repository=r, branch="user", last_commit="1234", status="SUCCESS")
        s.save()
        Vulnerability(
            details="1",
            scan=s,
            level=3,
            tool="Tool1",
            author_email="user@vulner.org",
            path="/src/file1",
            rule="VULN_1",
            commit_id="SHA11",
            is_new=True,
        ).save()
        Vulnerability(
            details="2",
            scan=s,
            level=3,
            tool="Tool2",
            author_email="user@vulner.org",
            path="/src/file2",
            rule="VULN_2",
            commit_id="SHA12",
            is_new=False,
        ).save()
        s.update_vulnerability_count()
        login(client, "user", "user")
        res = jget(client, "/api/scans/" + str(s.uuid)).json()
        self.assertEqual(res['new_error_count'], 1)
        self.assertEqual(res['new_warning_count'], 0)
        self.assertEqual(res['new_none_count'], 0)
        self.assertEqual(res['new_note_count'], 0)
        self.assertEqual(res['error_count'], 2)
        self.assertEqual(res['warning_count'], 0)
        self.assertEqual(res['none_count'], 0)
        self.assertEqual(res['note_count'], 0)
        logout(client)
        client.defaults['HTTP_REPOSITORY'] = str(r.authkey)
        asserts(self, jget(client, "/api/scans/" + str(s.uuid)), status=200, json_contains={"status": "SUCCESS"})
