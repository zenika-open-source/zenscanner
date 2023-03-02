import uuid
import json
import os
import docker
from core.tests.utils import TaskTestCase
from core.tasks_modules.pullers.NoCreds import NoCreds


class ScannerBaseTestTestCase(TaskTestCase):

    def __init__(self, ScannerClass, name, **kwargs):
        self.ScannerClass = ScannerClass
        self.name = name
        self.url = kwargs.get('url', "https://github.com/zenscanner/public-testing")
        self.source_control = kwargs.get('source_control', "git")
        self.sarif_file = kwargs.get('sarif_file', "sarifs/{}/main/{}.json".format(
            self.url.split('/')[-1],
            self.name
        ))
        super().__init__()

    def run(self):
        repository = {
            "source_control": self.source_control,
            "url": self.url
        }
        wo = str(uuid.uuid4())
        puller = NoCreds(repository=repository, worker_token=wo)
        puller.run()
        scanner = self.ScannerClass(worker_token=wo)
        sarif = json.loads(scanner.run().decode())
        with open(os.path.join(os.path.dirname(__file__), self.sarif_file)) as sarif_test_file:
            sarif_content = json.load(sarif_test_file)

        self.assertEqual(sarif_content, sarif)
        docker.from_env().volumes.get(wo).remove()
