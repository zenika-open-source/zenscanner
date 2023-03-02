from django.test import Client
from core.tests.utils import jget, asserts
from core.tests.utils import create_user, login
from core.models import Repository, Scan, Vulnerability
from json import load, dumps
import os
import uuid
from core.tests.utils import TaskTestCase
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from unittest import mock

client = Client()


@mock.patch('celery.backends.base.Backend._ensure_not_eager', mock.MagicMock(return_value=None))
class VulnerabilitiesViewTestCase(TaskTestCase):

    def setUp(self):
        sarif_json = load(open(os.path.join(os.path.dirname(__file__), '../../tests/workers/test1.sarif'), 'r'))
        user = create_user("user", "user", "user")
        user2 = create_user("user2", "user2", "user2")
        for i in range(25):
            r = Repository(name="{}".format(i), url="https://github.com/user/repo{}".format(i), owner=user)
            r.save()
            s = Scan(repository=r, branch="user1", last_commit="SHA1{}".format(i % 4))
            s.save()
            v = Vulnerability(
                details="{}".format(i),
                scan=s,
                level=3 if i % 5 == 0 else 0,
                tool="Tool1" if i % 3 == 0 else "Tool2",
                author_email="user{}@vulner.org".format(i % 4),
                path="{}file{}".format(("file:///src/" if i % 2 == 0 else ""), i % 4),
                rule="VULN_{}".format(i % 4),
                commit_id="SHA1{}".format(i % 4),
                is_new=(i % 9 == 0),
                sarif=dumps(sarif_json['runs'][0]['results'][0])

            )
            v.save()
            v.created_at = make_aware(datetime.now() + timedelta(days=-i))
            v.save()
        for i in range(25):
            r = Repository(name="user2", url="https://github.com/user/repo{}".format(i), owner=user2)
            r.save()
            s = Scan(repository=r, branch="user2")
            s.save()
            Vulnerability(details="{}".format(i), scan=s).save()

    def test_user_can_view_vuln_without_link(self):
        user = create_user("user3", "user3", "user3")
        r = Repository(name="user3", url="https://example.com/toto", owner=user, source_control='svn')
        r.save()
        s = Scan(repository=r, branch="trunk")
        s.save()
        v = Vulnerability(details="test", scan=s)
        v.save()
        self.assertEqual(v.commit_url, '')
        self.assertEqual(v.vulnerability_url, '')

    def test_user_can_view_locations(self):
        vuln = Vulnerability.objects.all()[0]
        self.assertEqual(vuln.locations, [{'physicalLocation': {'artifactLocation': {'uri': 'example.txt'}}}])

    def test_user_can_view_vuln_with_link(self):
        user = create_user("user3", "user3", "user3")
        r = Repository(name="user3", url="https://plugins.svn.wordpress.org/dummy-repo", owner=user, source_control='svn')
        r.save()
        s = Scan(repository=r, branch="trunk")
        s.save()
        v = Vulnerability(details="test", scan=s, path="readme.txt")
        v.save()
        self.assertEqual(v.commit_url, 'https://plugins.svn.wordpress.org/dummy-repo/trunk/')
        self.assertEqual(v.vulnerability_url, 'https://plugins.svn.wordpress.org/dummy-repo/trunk/readme.txt')
        s = Scan(repository=r, branch="test_branch_name")
        s.save()
        v = Vulnerability(details="test", scan=s, path="/readme.txt")
        v.save()
        self.assertEqual(v.commit_url, 'https://plugins.svn.wordpress.org/dummy-repo/branches/test_branch_name/')
        self.assertEqual(v.vulnerability_url, 'https://plugins.svn.wordpress.org/dummy-repo/branches/test_branch_name/readme.txt')

    def test_user_can_list_all_vuln_that_belongs_to_him(self):
        login(client, "user", "user")
        res = jget(client, "/api/vulnerabilities").json()
        self.assertEqual(res['count'], 25)
        self.assertEqual(len(res['items']), 10)

        asserts(self, jget(client, "/api/vulnerabilities?tool=Tool2"), json_contains={'count': 16})
        asserts(self, jget(client, "/api/vulnerabilities?tool=Tool2&tool=Tool1"), json_contains={'count': 25})

        res = jget(client, "/api/vulnerabilities?level=3&tool=Tool1").json()
        for item in res['items']:
            path = item['path']
            self.assertEqual(item['vulnerability_url'].replace('/tree/', '/commit/'), item['commit_url'] + (path if path.startswith('/') else "/" + path))
            self.assertEqual(item['level'], 3)
            self.assertEqual(item['tool'], 'Tool1')
            self.assertEqual(item['path'].startswith('file:///src'), False)
            self.assertEqual(item['locations'], [{'physicalLocation': {'artifactLocation': {'uri': 'example.txt'}}}])

        res = jget(client, "/api/vulnerabilities?level=3&level=1").json()
        for item in res['items']:
            self.assertEqual(item['level'] in [3, 1], True)
            self.assertEqual(item.get('sarif'), None)
            asserts(self, jget(client, "/api/vulnerabilities/" + item['uuid'] + "/sarif"), status=200, json_contains={"level": "error"})

        res = jget(client, "/api/vulnerabilities?details=1").json()
        for item in res['items']:
            self.assertEqual("1" in item['details'], True)

        res = jget(client, "/api/vulnerabilities?author_email=1").json()
        for item in res['items']:
            self.assertEqual("1" in item['author_email'], True)

        res = jget(client, "/api/vulnerabilities?path=1").json()
        for item in res['items']:
            self.assertEqual("1" in item['path'], True)

        res = jget(client, "/api/vulnerabilities?rule=1").json()
        for item in res['items']:
            self.assertEqual("1" in item['rule'], True)

        asserts(self, jget(client, "/api/vulnerabilities?new=1"), json_contains={"count": 3})
        asserts(self, jget(client, "/api/vulnerabilities?new=0"), json_contains={"count": 22})

    def test_user_can_list_vuln_by_scan_id(self):
        login(client, "user", "user")
        for scan in Scan.objects.all():
            if scan.branch == "user2":
                asserts(self, jget(client, "/api/vulnerabilities?scan=" + str(scan.uuid)), json_contains={"count": 0})
            else:
                res = jget(client, "/api/vulnerabilities?scan=" + str(scan.uuid)).json()
                self.assertEqual(res['count'], 1)
                self.assertEqual(res['items'][0]['repository']['url'], scan.repository.url)

    def test_user_can_get_vuln_by_uuid(self):
        login(client, "user", "user")
        asserts(self, jget(client, "/api/vulnerabilities/" + str(uuid.uuid4())), status=404)
        scan = Scan.objects.all()[0]
        asserts(self, jget(client, "/api/vulnerabilities/" + str(scan.vulnerability_set.all()[0].uuid)), status=200)

    def test_user_can_list_recent_vulns(self):
        login(client, "user", "user")
        asserts(self, jget(client, "/api/vulnerabilities?days=1"), json_contains={"count": 1})
        asserts(self, jget(client, "/api/vulnerabilities?days=-1"), status=422)
        asserts(self, jget(client, "/api/vulnerabilities?days=a"), status=422)
        asserts(self, jget(client, "/api/vulnerabilities?days=7"), json_contains={"count": 7})
