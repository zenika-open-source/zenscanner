from django.test import TestCase
from core.tasks_modules.pullers.NoCredsSvn import NoCredsSvn
import pytest
import docker
from core.utils.tasks import execute_command_in_volume


@pytest.mark.docker
class NoCredsSvnPullerTestCase(TestCase):

    def tearDown(self):
        try:
            docker.from_env().volumes.get('nocredssvn-puller-wk').remove()
        except docker.errors.NotFound:
            pass

    def test_nocredssvn_puller(self):

        self.assertEqual(NoCredsSvn(credential={"type": "dummy"}, pull_url="dummy").is_runnable(), False)
        self.assertEqual(NoCredsSvn(pull_url="dummy").is_runnable(), False)
        self.assertEqual(NoCredsSvn(repository={"source_control": "dummy"}).is_runnable(), False)

        puller = NoCredsSvn(
            worker_token="nocredssvn-puller-wk",
            repository={
                "url": "https://github.com/zenscanner/public-testing",
                "source_control": "svn"
            },
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"README.md" in execute_command_in_volume('nocredssvn-puller-wk', ["ls"]).output)

    def test_nocredssvn_puller_with_branch(self):

        puller = NoCredsSvn(
            worker_token="nocredssvn-puller-wk",
            repository={
                "url": "https://github.com/zenscanner/public-testing",
                "source_control": "svn"
            },
            branch='branches/test'
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        self.assertTrue(b"README.md" in execute_command_in_volume('nocredssvn-puller-wk', ["ls"]).output)

    def test_nocredssvn_puller_well_raise_on_error(self):
        puller = NoCredsSvn(
            worker_token="nocredssvn-puller-wk",
            repository={
                "url": "https://zenika.com",
                "source_control": "svn"
            },
        )

        self.assertEqual(puller.is_runnable(), True)
        with pytest.raises(Exception, match="Can't pull repository"):
            puller.run()
