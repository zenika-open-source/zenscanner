from django.test import TestCase
from core.models import Credential


def get_cred():
    return Credential(type="PublicSvn").get_instance()


class CredentialsPublicSvnTestCase(TestCase):

    def test_credential_validate(self):
        self.assertFalse(get_cred().validate())

    def test_credential_can_list_branch(self):
        cred = get_cred()
        branches = cred.list_branches('https://github.com/zenscanner/public-testing')
        self.assertEqual(branches, ['trunk', 'branches/test'])

    def test_last_commit_branches(self):
        cred = get_cred()
        result = cred.get_last_commit_for_branches('https://github.com/zenscanner/public-testing')
        self.assertEqual(result, [
            {'last_commit': '5', 'name': 'trunk'},
            {'last_commit': '7', 'name': 'branches/test'}
        ])
