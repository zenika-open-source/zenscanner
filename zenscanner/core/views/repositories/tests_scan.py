import json
from unittest import mock
from core.models import Repository, ScanResult, WorkerToken, Scan
from core.tests.utils import jpost, RequestMockPatcher, create_user, login, TaskTestCase
from django.test import Client, override_settings, tag
import pytest

client = Client()

API_URL = "http://testserver"

rmp = RequestMockPatcher(client, API_URL)


@mock.patch('celery.backends.base.Backend._ensure_not_eager', mock.MagicMock(return_value=None))
@override_settings(WEBUI_URI="http://testserver")
@pytest.mark.docker
class ScanTestCase(TaskTestCase):

    @tag('docker')
    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    def test_run_manual_scan_task(self, m, m2, m3):
        user = create_user("user", "user@zenscanner.test", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        login(client, "user", "user")
        task_id = jpost(client, "/api/repositories/{}/scan".format(repo.uuid), {}).json()['task_id']
        sr = ScanResult.objects.get(repository=repo, branch="main", task_id=task_id)
        runs = json.loads(sr.sarif)['runs']
        self.assertGreater(len(json.loads(sr.sarif)['runs'][0]["results"]), 0)
        for run in runs:
            self.assertGreater(len(run["results"]), 0)
        self.assertEqual(len([run['tool']['driver']['name'] for run in runs]), 4)
        scan = Scan.objects.get(uuid=task_id)
        self.assertEqual(WorkerToken.objects.filter(scan=scan).count(), 0)
        self.assertNotEqual(scan.last_commit, "")
        s = Scan.objects.get(uuid=sr.task_id)
        self.assertNotEqual(s.scanners, [])

    @tag('docker')
    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    def test_run_manual_scan_task_with_branch(self, m, m2, m3):
        user = create_user("user", "user@zenscanner.test", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user, source_control="svn")
        repo.save()
        login(client, "user", "user")
        task_id = jpost(client, "/api/repositories/{}/scan".format(repo.uuid), {"branch": "branches/test"}).json()['task_id']
        sr = ScanResult.objects.get(repository=repo, branch="test", task_id=task_id)
        self.assertGreater(len(json.loads(sr.sarif)['runs'][0]["results"]), 0)
        scan = Scan.objects.get(uuid=task_id)
        self.assertEqual(WorkerToken.objects.filter(scan=scan).count(), 0)
        self.assertNotEqual(scan.last_commit, "")
        s = Scan.objects.get(uuid=sr.task_id)
        self.assertNotEqual(s.scanners, [])
