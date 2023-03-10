from core.celery import sync_repositories
from core.models import Credential, Repository, Branch
from core.tests.utils import create_user, TaskTestCase
from django.test import Client, tag
from unittest import mock

client = Client()


@mock.patch('celery.backends.base.Backend._ensure_not_eager', mock.MagicMock(return_value=None))
class CredentialsSyncCase(TaskTestCase):

    @tag('docker')
    def test_run_manual_scan_task_with_credentials(self):
        user = create_user("user", "user", "user")
        cred = Credential(label="Github", type="Github", raw_value="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", owner=user)
        cred.save()
        self.assertEqual(0, Repository.objects.count())
        task = sync_repositories.delay()
        self.assertEqual('SUCCESS', sync_repositories.AsyncResult(task.id).state)
        self.assertGreater(Repository.objects.count(), 1)
        self.assertGreater(Branch.objects.count(), 0)

    @tag('docker')
    def test_run_manual_scan_task_with_credentials_and_disabled_sync(self):
        user = create_user("user", "user", "user")
        cred = Credential(label="Github", type="Github", raw_value="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", owner=user, allow_sync=False)
        cred.save()
        self.assertEqual(0, Repository.objects.count())
        task = sync_repositories.delay()
        self.assertEqual('SUCCESS', sync_repositories.AsyncResult(task.id).state)
        self.assertEqual(0, Repository.objects.count())
