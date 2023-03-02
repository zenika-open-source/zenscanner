from django.test import TestCase
from core.tasks_modules.pullers.Uploaded import Uploaded
import pytest
import docker
import os
import shutil
import tarfile
from core.utils.tasks import execute_command_in_volume
from core.tests.utils import RequestMockPatcher, create_user
from unittest import mock
from django.test import Client, override_settings
from core.models import WorkerToken, Repository, Scan


REPO_UUID = "b2046d7b-3490-46dc-9c55-a4dbcbbb7808"
SCAN_UUID = "895d8cd4-caf0-4022-8a1a-41ecb609b4dc"
WORKER_TOKEN = "1056e9c9-ffd9-42df-bde4-365b0bd1cbbf"
TEST_TGZ_LOCATION = os.path.join("/tmp/zenscanner/", REPO_UUID, SCAN_UUID + ".tgz")
API_URL = "http://testserver"

rmp = RequestMockPatcher(Client(), API_URL)

localdir = os.getcwd()


def create_test_tgz():
    os.makedirs(os.path.join("/tmp/zenscanner/", REPO_UUID), exist_ok=True)
    with open("/tmp/zenscanner_testfile.txt", "w") as src_file:
        src_file.write('dummy_file')
    os.chdir('/tmp')
    with tarfile.open(TEST_TGZ_LOCATION, "w:gz") as tar:
        tar.add("zenscanner_testfile.txt")
    user = create_user("user", "user", "user")
    repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user, uuid=REPO_UUID)
    repo.save()
    scan = Scan(repository=repo, uuid=SCAN_UUID)
    scan.save()
    worker_token = WorkerToken(scan=scan, token=WORKER_TOKEN)
    worker_token.save()
    os.chdir(localdir)


def remove_created_test_tgz():
    os.remove("/tmp/zenscanner_testfile.txt")
    os.remove(TEST_TGZ_LOCATION)
    if os.path.isdir("/tmp/zenscanner"):
        shutil.rmtree("/tmp/zenscanner")


@pytest.mark.docker
class NoUploadedPullerTestCase(TestCase):

    def tearDown(self):
        remove_created_test_tgz()
        try:
            docker.from_env().volumes.get(REPO_UUID).remove()
        except docker.errors.NotFound:
            pass

    def setUp(self):
        create_test_tgz()

    @override_settings(API_URL="http://testserver")
    @mock.patch('core.tasks_modules.pullers.Uploaded.requests.get', side_effect=rmp.mock_get)
    def test_uploaded_puller_uploader(self, m1):

        self.assertEqual(Uploaded(credential={"type": "dummy"}).is_runnable(), False)
        puller = Uploaded(
            worker_token=WORKER_TOKEN,
            pull_url="/api/workers/download"
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"./zenscanner_testfile" in execute_command_in_volume(WORKER_TOKEN, ["find"]).output)

    def test_uploaded_puller_well_raise_on_error(self):
        puller = Uploaded(
            worker_token="uploadedsvn-puller-wk",
            pull_url="http://zenika.com"
        )

        self.assertEqual(puller.is_runnable(), True)
        with pytest.raises(Exception, match="Can't pull repository"):
            puller.run()

    def test_uploaded_puller_well_raise_on_error_with_bad_url(self):
        puller = Uploaded(
            worker_token="uploadedsvn-puller-wk",
            pull_url="/fakepath"
        )

        self.assertEqual(puller.is_runnable(), True)
        with pytest.raises(Exception, match="Can't pull repository"):
            puller.run()
