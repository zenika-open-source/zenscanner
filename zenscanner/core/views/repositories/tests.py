from django.test import TestCase, Client
from core.tests.utils import jpost, jput, jget, jdelete, asserts
from core.tests.utils import create_user_and_login

import uuid

client = Client()


class ReposViewTestCase(TestCase):

    def test_user_can_add_repository(self):
        create_user_and_login(client, "user", "user", "user")
        token = asserts(self, jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Github",
            "value": "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"
        }), status=200).json()['uuid']

        repo = asserts(self, jpost(client, "/api/repositories", {
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': str(uuid.uuid4())
        }), status=404).json()

        repo = asserts(self, jpost(client, "/api/repositories", {
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': token,
        }), status=200).json()

        asserts(self, jget(client, "/api/repositories/" + str(uuid.uuid4())), status=404)
        asserts(self, jget(client, "/api/repositories/" + repo['uuid']), status=200, json={
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': token,
            'scan_count': 0,
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': [],
            'source_control': 'git'
        })

        asserts(self, jget(client, "/api/repositories"), status=200, json={"items": [{
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': token,
            'scan_count': 0,
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': [],
            'source_control': 'git'
        }], "count": 1})

        asserts(self, jget(client, "/api/repositories/" + repo['uuid'] + "?refresh_branches"), status=200, json={
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': token,
            'scan_count': 0,
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': ['main', 'test-scan-branch'],
            'source_control': 'git'
        })

    def test_user_can_sync_svn_branches(self):
        create_user_and_login(client, "user", "user", "user")

        repo = asserts(self, jpost(client, "/api/repositories", {
            'name': 'Test Repo',
            'url': 'https://plugins.svn.wordpress.org/easy-career-openings',
            'source_control': 'svn'
        }), status=200).json()

        asserts(self, jget(client, "/api/repositories/" + repo['uuid'] + "?refresh_branches"), status=200, json={
            'name': 'Test Repo',
            'url': 'https://plugins.svn.wordpress.org/easy-career-openings',
            'scan_count': 0,
            'credential': '',
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': ['trunk'],
            'source_control': 'svn'
        })

    def test_user_can_edit_repository(self):
        create_user_and_login(client, "user", "user", "user")
        cred = asserts(self, jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Github",
            "value": "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"
        }), status=200).json()

        repo_token = asserts(self, jpost(client, "/api/repositories", {
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/test-private-repo',
            'credential': cred['uuid']
        }), status=200).json()['uuid']
        new_data = {
            'name': 'test',
            'url': 'test',
            'scan_count': 0,
            'credential': ''
        }
        asserts(self, jput(client, "/api/repositories/" + repo_token, new_data), status=200, json_contains={
            'name': 'test',
            'url': 'test',
            'credential': ''
        })
        cred2 = asserts(self, jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Github",
            "value": "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"
        }), status=200).json()
        new_data['credential'] = cred2['uuid']
        asserts(self, jput(client, "/api/repositories/" + repo_token, new_data), status=200, json_contains={
            'credential': cred2['uuid']
        })

        asserts(self, jput(client, "/api/repositories/" + str(uuid.uuid4()), new_data), status=404)

    def test_user_can_delete_repo(self):
        self.test_user_can_add_repository()
        repo_uuid = jget(client, "/api/repositories").json()['items'][0]['uuid']
        asserts(self, jdelete(client, "/api/repositories/" + repo_uuid), status=200)
        asserts(self, jget(client, "/api/repositories"), status=200, json=[])
        asserts(self, jdelete(client, "/api/repositories/" + repo_uuid), status=404)

    def test_user_can_add_repository_without_credentials(self):
        create_user_and_login(client, "user", "user", "user")
        repo = asserts(self, jpost(client, "/api/repositories", {
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/public-testing',
            'source_control': 'git'
        }), status=200).json()
        asserts(self, jget(client, "/api/repositories/" + repo['uuid']), status=200, json={
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/public-testing',
            'scan_count': 0,
            'credential': '',
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': [],
            'source_control': 'git'
        })

        asserts(self, jget(client, "/api/repositories"), status=200, json={"items": [{
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/public-testing',
            'scan_count': 0,
            'credential': '',
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': [],
            'source_control': 'git'
        }], "count": 1})

        asserts(self, jget(client, "/api/repositories/" + repo['uuid'] + "?refresh_branches"), status=200, json={
            'name': 'Test Repo',
            'url': 'https://github.com/zenscanner/public-testing',
            'scan_count': 0,
            'credential': '',
            'uuid': repo['uuid'],
            'authkey': repo['authkey'],
            'branches': ['main', 'test'],
            'source_control': 'git'
        })
