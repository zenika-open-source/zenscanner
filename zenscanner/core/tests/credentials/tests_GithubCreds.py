from django.test import TestCase
from core.models import Credential


def get_cred():
    return Credential(type="Github", raw_value="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").get_instance()


class CredentialsGithubTestCase(TestCase):

    def test_credential_validate(self):
        self.assertTrue(get_cred().validate())
        self.assertFalse(Credential(type="Github", raw_value="dzajoj").get_instance().validate())

    def test_credential_can_list_branch(self):
        cred = get_cred()
        branches = cred.list_branches('https://github.com/zenscanner/test-private-repo')
        self.assertEqual(branches, ['main', 'test-scan-branch'])
        branches = cred.list_branches('https://github.com/zenscanner/test-private-repo.git')
        self.assertEqual(branches, ['main', 'test-scan-branch'])
        branches = cred.list_branches('https://github.com/non/existing/repo')
        self.assertEqual(branches, [])

    def test_last_commit_branches(self):
        cred = get_cred()
        result = cred.get_last_commit_for_branches('https://github.com/zenscanner/test-private-repo')
        self.assertEqual(result, [
            {'last_commit': '5ca148c48d1dc68e68b4e9641cf327ba711a7027', 'name': 'main'},
            {'last_commit': '09adbac693a54a12d1f3c1e63fff4c32ed104bbb', 'name': 'test-scan-branch'}
        ])
        result = cred.get_last_commit_for_branches('https://github.com/non/existing/repo')
        self.assertEqual(result, [])

    def test_list(self):
        result = get_cred().list()
        self.assertGreater(len(result), 0)
