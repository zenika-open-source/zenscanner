from django.test import TestCase, Client, override_settings
from core.tests.utils import asserts, create_user, jget, login, jput, logout
from core.models import Repository, ScanResult, WorkerToken, Scan
import uuid
from django.conf import settings

from django.core import mail
import json

client = Client()

sarif_content = """{"version":"2.1.0","runs":[{"tool":{"driver":{"name":"Example Tool"}},"results":[{"ruleId":"Example Rule","level":"error","locations":[{"physicalLocation":{"artifactLocation":{"uri":"example.txt"}}}],"message":{"text":"Welcome to the online SARIF Viewer demo. Drag and drop a SARIF file here to view."},"baselineState":"new"}]}]}"""


@override_settings(WEBUI_URI="http://testserver")
class ResultViewTestCase(TestCase):

    def test_duplicate_vulnerability(self):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        scan = Scan(repository=repo)
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, jput(client, "/api/workers/information", {"branch": "master", "last_commit": "1234"}), status=200)
        asserts(self, client.put("/api/workers/result", data=sarif_content), status=200)
        scan2 = Scan(repository=repo, status='PENDING', branch="master")
        scan2.save()
        worker_token2 = WorkerToken(scan=scan2)
        worker_token2.save()
        client.defaults['HTTP_WORKER'] = str(worker_token2.token)
        asserts(self, client.put("/api/workers/result", data=sarif_content), status=200)
        logout(client)
        login(client, "user", "user")
        asserts(self,
                jget(client, "/api/scans/{}/result".format(scan.uuid)),
                status=200,
                json_contains={"branch": "master", 'error_count': 1, 'new_error_count': 1},
                )
        asserts(self,
                jget(client, "/api/scans/{}/result".format(scan2.uuid)),
                status=200,
                json_contains={"branch": "master", 'error_count': 1},
                )
        repo = Repository(name="Test2 Repo", url='https://github.com/zenscanner/public-testing2', owner=user)
        repo.save()
        scan = Scan(repository=repo, branch="master")
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, client.put("/api/workers/result", data=sarif_content), status=200)
        logout(client)
        login(client, "user", "user")
        asserts(self,
                jget(client, "/api/scans/{}/result".format(scan.uuid)),
                status=200,
                json_contains={"branch": "master", 'error_count': 1, 'new_error_count': 1},
                )

    def test_user_can_access_scan_result(self):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        authkey = repo.authkey
        scan = Scan(repository=repo)
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        logout(client)
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, jput(client, "/api/workers/information", {"branch": "master", "last_commit": "1234"}), status=200)
        asserts(self, client.put("/api/workers/result", data=sarif_content), status=200)
        logout(client)
        login(client, "user", "user")
        asserts(self,
                jget(client, "/api/scans/{}/result".format(scan.uuid)),
                status=200,
                json_contains={"branch": "master", 'error_count': 1, 'new_error_count': 1},
                )
        asserts(self, jget(client, "/api/scans/{}/result".format(uuid.uuid4())), status=404)
        user = create_user("user2", "user2", "user2")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        task_id = uuid.uuid4()
        sr = ScanResult(repository=repo, task_id=task_id, branch="master", sarif="SARIF")
        sr.save()
        asserts(self, jget(client, "/api/scans/{}/result".format(task_id)), status=404)
        logout(client)
        client.defaults['HTTP_REPOSITORY'] = str(authkey)
        asserts(self,
                jget(client, "/api/scans/{}/result".format(scan.uuid)),
                status=200,
                json_contains={"branch": "master", 'error_count': 1, 'new_error_count': 1},
                )
        res = jget(client, "/api/scans/" + str(scan.uuid) + "/sarif")
        asserts(self, res, status=200)
        self.assertGreater(len(res.json()['runs']), 0)

    def test_scan_export_to_mail(self):
        user = create_user("user", "user@zenscanner.test", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        scan = Scan(repository=repo)
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        logout(client)
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, jput(client, "/api/workers/information", {"branch": "main", "last_commit": "1234"}), status=200)
        asserts(self, client.put("/api/workers/result", data=sarif_content), status=200)
        asserts(self, client.delete("/api/workers"), status=200)
        self.assertEqual(WorkerToken.objects.filter(scan=scan).count(), 0)
        self.assertEqual(mail.outbox[0].subject, "[ZenScanner] Scan finished for Test Repo (main) 1 new vulnerabilities")
        self.assertEqual(mail.outbox[0].to, ["user@zenscanner.test"])
        self.assertIn("(1 new) vulnerabilities.", mail.outbox[0].body)
        self.assertEqual(scan.new_error_count, 0)
        self.assertEqual(scan.new_warning_count, 0)
        self.assertEqual(scan.new_note_count, 0)
        self.assertEqual(scan.new_none_count, 0)
        self.assertIn("{}/scan/{}".format(settings.WEBUI_URI, scan.uuid), mail.outbox[0].body)
        self.assertEqual(len(mail.outbox), 1)
        login(client, "user", "user")
        scans = jget(client, "/api/repositories/{}/scans".format(repo.uuid)).json()
        self.assertEqual(len(scans['items']), 1)
        self.assertEqual(scans['items'][0]['uuid'], str(scan.uuid))
        self.assertEqual(scans['items'][0]['branch_url'], "https://github.com/zenscanner/public-testing/tree/main")
        self.assertEqual(scans['items'][0]['commit_url'], "https://github.com/zenscanner/public-testing/commit/1234")
        self.assertEqual(scans['items'][0]['scanners'], ["Example Tool"])
        self.assertEqual(scans['items'][0]['matched_scanners'], {'old': [], 'new': ['Example Tool']})
        self.assertEqual(scans['items'][0]['status'], 'SUCCESS')
        repo = Repository.objects.get(uuid=repo.uuid)
        self.assertEqual(repo.scan_count, 1)

    def test_scan_sarif_snippet_max_size(self):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        scan = Scan(repository=repo)
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        scan = Scan(repository=repo, status='PENDING', branch="master")
        scan.save()
        logout(client)
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        content = json.loads(sarif_content)
        content['runs'][0]['results'][0]['locations'][0]['physicalLocation']['region'] = {"snippet": {"text": "A" * 1000}}
        asserts(self, jput(client, "/api/workers/information", {"branch": "master", "last_commit": "1234"}), status=200)
        asserts(self, client.put("/api/workers/result", data=json.dumps(content)), status=200)
        sr = ScanResult.objects.get(repository=repo, branch="master")
        self.assertLess(len(json.loads(sr.sarif)['runs'][0]['results'][0]['locations'][0]['physicalLocation']['region']['snippet']['text']), 100)
