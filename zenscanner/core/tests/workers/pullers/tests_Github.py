from django.test import TestCase
from core.tasks_modules.pullers.Github import Github
import pytest
import docker
from core.utils.tasks import execute_command_in_volume


@pytest.mark.docker
class GithubPullerTestCase(TestCase):

    def tearDown(self):
        try:
            docker.from_env().volumes.get('github-puller-wk').remove()
        except docker.errors.NotFound:
            pass

        try:
            docker.from_env().volumes.get('github-puller-wk-home').remove()
        except docker.errors.NotFound:
            pass

    def test_github_puller(self):

        self.assertEqual(Github().is_runnable(), False)
        self.assertEqual(Github(credential={"type": "Github"}, pull_url="dummy").is_runnable(), False)

        puller = Github(
            credential={
                "value": "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",
                "type": "Github"
            },
            worker_token="github-puller-wk",
            repository={"url": "https://github.com/zenscanner/test-private-repo"}
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        with pytest.raises(docker.errors.NotFound):
            docker.from_env().volumes.get('github-puller-wk-home')
        self.assertTrue(b"README.md" in execute_command_in_volume('github-puller-wk', ["ls"]).output)

    def test_github_puller_with_branch(self):

        puller = Github(
            credential={
                "value": "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",
                "type": "Github"
            },
            worker_token="github-puller-wk",
            repository={"url": "https://github.com/zenscanner/test-private-repo"},
            branch='test-scan-branch'
        )

        self.assertEqual(puller.is_runnable(), True)
        puller.run()
        with pytest.raises(docker.errors.NotFound):
            docker.from_env().volumes.get('github-puller-wk-home')
        self.assertTrue(b"README.md" in execute_command_in_volume('github-puller-wk', ["ls"]).output)

    def test_github_puller_well_remove_volumes_on_error(self):
        puller = Github(
            credential={
                "value": "test",
                "type": "Github"
            },
            worker_token="github-puller-wk",
            repository={"url": "http://zenika.com"}
        )

        self.assertEqual(puller.is_runnable(), True)
        with pytest.raises(Exception, match="Can't pull repository"):
            puller.run()

        with pytest.raises(docker.errors.NotFound):
            docker.from_env().volumes.get('github-puller-wk-home')
