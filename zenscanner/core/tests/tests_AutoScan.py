from core.models import WorkerToken
from core.celery import autoscan
from core.models import Credential, Repository, Scan, Branch
from core.tests.utils import create_user, RequestMockPatcher, TaskTestCase
from django.test import Client, tag
from unittest import mock

client = Client()

API_URL = "http://testserver"

rmp = RequestMockPatcher(client, API_URL)


def run_scan(worker_token, **kwargs):
    wt = WorkerToken.objects.get(token=worker_token)
    wt.scan.last_commit = "1234"
    wt.scan.save()


@mock.patch('core.celery.run_scan.delay', side_effect=run_scan)
@mock.patch('celery.backends.base.Backend._ensure_not_eager', mock.MagicMock(return_value=None))
class AutoScanCase(TaskTestCase):

    @tag('docker')
    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    def test_scan_can_be_automatically_start(self, m, m2, m3, m4):
        user = create_user("user", "user", "user")
        cred = Credential(label="Github", type="Github", raw_value="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", owner=user)
        cred.save()
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', credential=cred, owner=user)
        repo.save()
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans = Scan.objects.all()
        self.assertGreater(len(scans), 0)
        for scan in scans:
            scan.last_commit = ""
            scan.save()
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans2 = Scan.objects.all()
        self.assertEqual(len(scans2), len(scans) * 2)
        branches = Branch.objects.all()
        self.assertEqual(['main', 'test-scan-branch'], [b.name for b in branches])
        self.assertGreater(len(branches), 0)

    @tag('docker')
    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    def test_scan_can_be_automatically_start_for_svn(self, m, m2, m3, m4):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user, source_control='svn')
        repo.save()
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans = Scan.objects.all()
        self.assertGreater(len(scans), 0)
        for scan in scans:
            scan.last_commit = ""
            scan.save()
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans2 = Scan.objects.all()
        self.assertEqual(len(scans2), len(scans) * 2)
        branches = Branch.objects.all()
        self.assertEqual(['trunk', 'branches/test'], [b.name for b in branches])
        self.assertGreater(len(branches), 0)

    @tag('docker')
    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    def test_scan_can_be_automatically_start_without_creds(self, m, m2, m3, m4):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/public-testing', owner=user)
        repo.save()
        self.assertEqual(repo.credential.get_instance().get_last_commit_for_branches('https://github.com/zenscanner/public-testing'), [
            {'name': 'main', 'last_commit': 'c5be0ac0550b9e5d36595fe006c7fd604f6ffc6b'},
            {'name': 'test', 'last_commit': '623172691164746073cebfeffab3d1e97648b3b6'}
        ])
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans = Scan.objects.all()
        self.assertGreater(len(scans), 0)
        for scan in scans:
            scan.last_commit = ""
            scan.save()
        task = autoscan.delay()
        self.assertEqual('SUCCESS', autoscan.AsyncResult(task.id).state)
        scans2 = Scan.objects.all()
        self.assertEqual(len(scans2), len(scans) * 2)
        branches = Branch.objects.all()
        self.assertGreater(len(branches), 0)
