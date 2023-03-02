from django.test import TestCase, Client, override_settings
from core.tests.utils import asserts, create_user, jget
import os
import tarfile
import hashlib
import pathlib
from core.models import Repository, WorkerToken, Scan
import shutil

client = Client()

REPO_UUID = "b2046d7b-3490-46dc-9c55-a4dbcbbb7808"
SCAN_UUID = "895d8cd4-caf0-4022-8a1a-41ecb609b4dc"
WORKER_TOKEN = "1056e9c9-ffd9-42df-bde4-365b0bd1cbbf"
TEST_TGZ_LOCATION = os.path.join("/tmp/zenscanner/", REPO_UUID, SCAN_UUID + ".tgz")


def create_test_tgz():
    os.makedirs(os.path.join("/tmp/zenscanner/", REPO_UUID), exist_ok=True)
    with open("/tmp/zenscanner_testfile.txt", "w") as src_file:
        src_file.write('dummy_file')
    with tarfile.open(TEST_TGZ_LOCATION, "w:gz") as tar:
        tar.add("/tmp/zenscanner_testfile.txt")
    user = create_user("user", "user", "user")
    repo = Repository(name="Test Repo", url='https://github.com/zenscanner/test-private-repo', owner=user, uuid=REPO_UUID)
    repo.save()
    scan = Scan(repository=repo, uuid=SCAN_UUID)
    scan.save()
    worker_token = WorkerToken(scan=scan, token=WORKER_TOKEN)
    worker_token.save()


def remove_created_test_tgz():

    os.remove("/tmp/zenscanner_testfile.txt")
    os.remove(TEST_TGZ_LOCATION)
    if os.path.isdir("/tmp/zenscanner"):
        shutil.rmtree("/tmp/zenscanner")


class ReposViewLocalTestCase(TestCase):

    def setUp(self):
        create_test_tgz()

    def tearDown(self):
        remove_created_test_tgz()

    def test_worker_can_download(self):
        client.defaults['HTTP_WORKER'] = WORKER_TOKEN
        resp = asserts(self, jget(client, "/api/workers/download"), status=200)
        md5src = hashlib.md5(pathlib.Path(TEST_TGZ_LOCATION).read_bytes()).hexdigest()
        md5dst = hashlib.md5(resp.content).hexdigest()
        self.assertEqual(md5src, md5dst)

    def test_worker_cant_download_removed_scan(self):

        client.defaults['HTTP_WORKER'] = WORKER_TOKEN
        Scan.objects.get(uuid=SCAN_UUID).delete()
        asserts(self, jget(client, "/api/workers/download"), status=401)

    @override_settings(UPLOAD_TYPE="notlocal")
    def test_worker_cant_download_if_s3(self):

        client.defaults['HTTP_WORKER'] = WORKER_TOKEN
        asserts(self, jget(client, "/api/workers/download"), status=404)
