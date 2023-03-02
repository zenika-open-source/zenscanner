from django.test import TestCase
from core.models import Credential


def get_cred():
    return Credential(type="PublicGit").get_instance()


class CredentialsPublicGitTestCase(TestCase):

    def test_credential_validate(self):
        self.assertFalse(get_cred().validate())

    def test_credential_can_list_branch(self):
        cred = get_cred()
        branches = cred.list_branches('https://github.com/zenscanner/public-testing')
        self.assertEqual(branches, ['main', 'test'])
        branches = cred.list_branches('https://github.com/zenscanner/public-testing.git')
        self.assertEqual(branches, ['main', 'test'])

    def test_last_commit_branches(self):
        cred = get_cred()
        result = cred.get_last_commit_for_branches('https://github.com/zenscanner/public-testing')
        self.assertEqual(result, [
            {'last_commit': 'c5be0ac0550b9e5d36595fe006c7fd604f6ffc6b', 'name': 'main'},
            {'last_commit': '623172691164746073cebfeffab3d1e97648b3b6', 'name': 'test'}
        ])
