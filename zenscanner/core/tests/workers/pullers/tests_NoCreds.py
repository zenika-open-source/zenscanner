from django.test import TestCase
from core.tasks_modules.pullers.NoCreds import NoCreds
import pytest
import docker
from core.utils.tasks import execute_command_in_volume


@pytest.mark.docker
class NoCredsPullerTestCase(TestCase):

    def tearDown(self):
        try:
            docker.from_env().volumes.get('nocreds-puller-wk').remove()
        except docker.errors.NotFound:
            pass

    def test_nocreds_puller(self):

        self.assertEqual(NoCreds(credential={"type": "dummy"}, pull_url="dummy").is_runnable(), False)
        self.assertEqual(NoCreds(pull_url="dummy").is_runnable(), False)
        self.assertEqual(NoCreds(repository={"source_control": "dummy"}).is_runnable(), False)

        puller = NoCreds(
            worker_token="nocreds-puller-wk",
            repository={
                "url": "https://github.com/zenscanner/public-testing",
                "source_control": "git"
            },
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"README.md" in execute_command_in_volume('nocreds-puller-wk', ["ls"]).output)

    def test_nocreds_puller_with_branch(self):

        puller = NoCreds(
            worker_token="nocreds-puller-wk",
            repository={
                "url": "https://github.com/zenscanner/public-testing",
                "source_control": "git"
            },
            branch='test'
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"README.md" in execute_command_in_volume('nocreds-puller-wk', ["ls"]).output)

    def test_nocreds_puller_well_raise_on_error(self):
        puller = NoCreds(
            worker_token="nocredssvn-puller-wk",
            repository={
                "url": "https://zenika.com",
                "source_control": "git"
            },
        )

        self.assertEqual(puller.is_runnable(), True)
        with pytest.raises(Exception, match="Can't pull repository"):
            puller.run()
