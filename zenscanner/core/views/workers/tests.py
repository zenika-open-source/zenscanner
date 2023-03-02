from django.test import TestCase, Client, override_settings
from core.tests.utils import jget, jdelete, asserts, create_user
from core.models import WorkerToken, Repository, Credential, Scan, ScanResult
from datetime import datetime, timedelta

client = Client()


@override_settings(USE_TZ=True)
class WorkerRootViewTestCase(TestCase):

    def test_worker_can_access_information(self):

        user = create_user("user", "user", "user")
        cred = Credential(label="Generic", type="Generic", raw_value="aaa", owner=user)
        cred.save()
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-bandit', owner=user, credential=cred,)
        repo.save()
        scan = Scan(repository=repo)
        scan.save()
        ScanResult(repository=repo, task_id=scan.uuid).save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()

        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, jget(client, "/api/workers/repository"), status=200, json_contains={
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-bandit',
            'source_control': 'git'
        })
        asserts(self, jget(client, "/api/workers/repository/credential"), status=200, json_contains={
            "label": "Generic",
            "type": "Generic",
            "value": "aaa"
        })

        asserts(self, jdelete(client, "/api/workers", {}), status=200)
        asserts(self, jget(client, "/api/workers/repository"), status=401)

        worker_token = WorkerToken(scan=scan, deleted_at=(datetime.now() + timedelta(days=-1)))
        worker_token.save()
        client.defaults['HTTP_WORKER'] = str(worker_token.token)
        asserts(self, jget(client, "/api/workers/repository"), status=401)
