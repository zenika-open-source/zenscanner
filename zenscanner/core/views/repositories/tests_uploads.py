from django.test import Client, override_settings, tag
from core.tests.utils import jget, asserts
from core.tests.utils import create_user, TaskTestCase, RequestMockPatcher, login
import os
import tarfile
import requests
import shutil
import uuid
from unittest import mock
from core.models import WorkerToken, Repository, Scan
from core.tasks_modules.pullers.Uploaded import Uploaded
from core.utils.tasks import execute_command_in_volume
import pytest


client = Client()

API_URL = "http://testserver"

rmp = RequestMockPatcher(client, API_URL)

localdir = os.getcwd()


class MinioMocker():

    def __init__(self, url, **kwargs):
        pass

    def bucket_exists(self, bucket_name):
        return os.path.isdir('/tmp/' + bucket_name)

    def make_bucket(self, bucket_name):
        return os.makedirs('/tmp/' + bucket_name)

    def remove_bucket(self, bucket_name):
        return shutil.rmtree('/tmp/' + bucket_name)

    def presigned_put_object(self, bucket_name, name):
        return "http://mockeds3/{}/{}".format(bucket_name, name)

    def presigned_get_object(self, bucket_name, name):
        return self.presigned_put_object(bucket_name, name)


s3client = MinioMocker(
    "dummy",
    access_key="dummy",
    secret_key="dummy",
    region="dummy",
)

S3_BUCKET_TEST_NAME = "uploadbucket"
TEST_TGZ_NAME = "zenscanner.tgz"
TEST_TGZ_LOCATION = os.path.join("/tmp", TEST_TGZ_NAME)
MOKED_KWARGS = {}


def create_test_bucket():
    if not s3client.bucket_exists(S3_BUCKET_TEST_NAME):
        s3client.make_bucket(S3_BUCKET_TEST_NAME)


def delete_test_bucket():

    s3client.remove_bucket(S3_BUCKET_TEST_NAME)


def create_test_tgz():
    with open("/tmp/zenscanner_testfile.txt", "w") as src_file:
        src_file.write('dummy_file')
    os.chdir('/tmp')
    with tarfile.open(TEST_TGZ_LOCATION, "w:gz") as tar:
        tar.add("zenscanner_testfile.txt")
    os.chdir(localdir)


def remove_created_test_tgz():
    os.remove("/tmp/zenscanner_testfile.txt")
    os.remove(TEST_TGZ_LOCATION)
    if os.path.isdir("/tmp/zenscanner"):
        shutil.rmtree("/tmp/zenscanner")


class TaskReturn:
    id = 1


def mock_task_call(*args, **kwargs):
    global MOKED_KWARGS
    MOKED_KWARGS = kwargs
    return TaskReturn()


class ReposViewLocalAsRepositoryTestCase(TaskTestCase):

    def setUp(self):
        create_test_tgz()

    def tearDown(self):
        remove_created_test_tgz()

    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    @mock.patch('core.tasks_modules.pullers.Uploaded.requests.get', side_effect=rmp.mock_get)
    @tag('docker')
    def test_user_can_upload_to_local_and_trigger_scan(self, m, m2, m3, m4):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user)
        repo.save()
        client.defaults['HTTP_REPOSITORY'] = str(repo.authkey)
        asserts(self, jget(
            client,
            "/api/repositories/{}/upload".format(repo.uuid)),
            status=200,
            json_contains={
                "type": "local",
                "url": "http://testserver/api/repositories/{}/upload".format(repo.uuid),
        })
        with open(TEST_TGZ_LOCATION, "rb") as tar:
            response = client.put("/api/repositories/{}/upload".format(repo.uuid), data=tar.read())
        scan = Scan.objects.get(uuid=response.json()['task_id'])
        wt = WorkerToken.objects.filter(scan=scan)
        self.assertTrue(len(wt) == 0)
        asserts(self, response, status=200).json()

    @override_settings(USE_X_FORWARDED_PORT=True)
    @override_settings(SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_user_can_upload_secure(self):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user)
        repo.save()
        client.defaults['HTTP_REPOSITORY'] = str(repo.authkey)
        client.defaults['HTTP_X_FORWARDED_PROTO'] = "https"
        client.defaults['HTTP_X_FORWARDED_PORT'] = 443
        res = client.get("/api/repositories/{}/upload".format(repo.uuid))
        self.assertEqual(res.json(), {
            "type": "local",
            "url": "https://testserver/api/repositories/{}/upload".format(repo.uuid),
        })
        del client.defaults['HTTP_X_FORWARDED_PROTO']


@override_settings(UPLOAD_TYPE="s3")
@override_settings(UPLOAD_ENDPOINT="dummy")
@override_settings(UPLOAD_ACCESS_KEY="dummy")
@override_settings(UPLOAD_SECRET_KEY="dummy")
@override_settings(UPLOAD_REGION="dummy")
@override_settings(UPLOAD_BUCKET=S3_BUCKET_TEST_NAME)
class ReposViewS3AsRepositoryTestCase(TaskTestCase):

    def setUp(self):
        create_test_tgz()
        create_test_bucket()

    def tearDown(self):
        remove_created_test_tgz()
        delete_test_bucket()

    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    @mock.patch('core.tasks_modules.pullers.Uploaded.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.views.repositories.utils.Minio', side_effect=MinioMocker)
    @tag('docker')
    def test_user_can_upload_to_s3(self, m, m2, m3, m4, m5):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user)
        repo.save()

        client.defaults['HTTP_REPOSITORY'] = str(repo.authkey)
        url = asserts(self, jget(client, "/api/repositories/{}/upload".format(repo.uuid)),
                      status=200,
                      json_contains={"type": "s3"}
                      ).json()['url']
        self.assertEqual(requests.put(url, data=open(TEST_TGZ_LOCATION, 'rb')).status_code, 200)
        with mock.patch('core.celery.run_uploaded_scan.apply_async', side_effect=mock_task_call) as m:
            client.put("/api/repositories/{}/upload".format(repo.uuid))

        self.assertEqual(m.called, True)


class ReposViewLocalTestCase(TaskTestCase):

    def setUp(self):
        create_test_tgz()

    def tearDown(self):
        remove_created_test_tgz()

    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    @mock.patch('core.tasks_modules.pullers.Uploaded.requests.get', side_effect=rmp.mock_get)
    @tag('docker')
    def test_user_can_upload_to_local(self, m, m2, m3, m4):

        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user)
        repo.save()

        login(client, "user", "user")
        asserts(self, jget(client, "/api/repositories/{}/upload".format(uuid.uuid4())), status=404)
        asserts(self, jget(
            client,
            "/api/repositories/{}/upload".format(repo.uuid)),
            status=200,
            json_contains={"type": "local"}
        )

        with open(TEST_TGZ_LOCATION, "rb") as tar:
            response = client.put("/api/repositories/{}/upload".format(uuid.uuid4()), data=tar.read())
            asserts(self, response, status=404)
            response = client.put("/api/repositories/{}/upload".format(repo.uuid), data="Dummy File")
            asserts(self, response, status=422)

        with mock.patch('core.celery.run_uploaded_scan.apply_async', side_effect=mock_task_call) as m:
            with open(TEST_TGZ_LOCATION, "rb") as tar:
                response = client.put("/api/repositories/{}/upload".format(repo.uuid), data=tar.read())
        scan = Scan.objects.get(uuid=response.json()['task_id'])
        wt = WorkerToken.objects.get(scan=scan)
        self.assertEqual(MOKED_KWARGS['args'], [wt.token, '/api/workers/download'])
        self.assertEqual(m.called, True)


@override_settings(UPLOAD_TYPE="s3")
@override_settings(UPLOAD_ENDPOINT="dummy")
@override_settings(UPLOAD_ACCESS_KEY="dummy")
@override_settings(UPLOAD_SECRET_KEY="dummy")
@override_settings(UPLOAD_REGION="dummy")
@override_settings(UPLOAD_BUCKET=S3_BUCKET_TEST_NAME)
@pytest.mark.docker
class ReposViewS3TestCase(TaskTestCase):

    def setUp(self):
        create_test_tgz()
        create_test_bucket()

    def tearDown(self):
        remove_created_test_tgz()
        delete_test_bucket()

    @mock.patch('core.utils.tasks.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.utils.tasks.requests.put', side_effect=rmp.mock_put)
    @mock.patch('core.utils.tasks.requests.delete', side_effect=rmp.mock_delete)
    @mock.patch('core.tasks_modules.pullers.Uploaded.requests.get', side_effect=rmp.mock_get)
    @mock.patch('core.views.repositories.utils.Minio', side_effect=MinioMocker)
    @tag('docker')
    def test_user_can_upload_to_s3(self, m, m2, m3, m4, m5):
        user = create_user("user", "user", "user")
        repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user)
        repo.save()

        login(client, "user", "user")
        url = asserts(self, jget(client, "/api/repositories/{}/upload".format(repo.uuid)),
                      status=200,
                      json_contains={"type": "s3"}
                      ).json()['url']
        self.assertEqual(requests.put(url, data=open(TEST_TGZ_LOCATION, 'rb')).status_code, 200)

        with mock.patch('core.celery.run_uploaded_scan.apply_async', side_effect=mock_task_call) as m:
            response = client.put("/api/repositories/{}/upload".format(repo.uuid))
        self.assertEqual(m.called, True)
        scan = Scan.objects.get(uuid=response.json()['task_id'])
        wt = WorkerToken.objects.get(scan=scan)
        puller = Uploaded(
            worker_token=str(wt.token),
            pull_url=url
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"./zenscanner_testfile" in execute_command_in_volume(wt.token, ["find"]).output)
