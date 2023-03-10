from django.test import TestCase, Client
from core.tests.utils import create_user_and_login, asserts, jpost, jget, jput, jdelete, login, create_user, logout
from uuid import uuid4
from core.models import Credential

client = Client()


class CredentialsViewTestCase(TestCase):

    def test_user_cannot_add_cred_with_invalid_cred_type(self):
        create_user_and_login(client, "user", "user", "user")

        asserts(self, jpost(client, "/api/credentials", {
                "label": "TestGit",
                "type": "Not a valid cred type",
                "value": "blblblblbl"
                }), status=422)

    def test_user_cannot_add_cred_with_empty_label(self):
        create_user_and_login(client, "user", "user", "user")

        asserts(self, jpost(client, "/api/credentials", {
                "label": "",
                "type": "Generic",
                "value": "blblblblbl"
                }), status=422)

    def test_user_can_add_valid_cred(self):
        create_user_and_login(client, "user", "user", "user")

        asserts(self, jpost(client, "/api/credentials", {
                "label": "Github",
                "type": "Generic",
                "value": "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"
                }), status=200)

    def test_user_can_delete_valid_cred(self):
        create_user_and_login(client, "user", "user", "user")

        uuid = jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Generic",
            "value": "Test Value 1234"
        }).json()['uuid']

        asserts(self, jdelete(client, "/api/credentials/" + uuid), status=200)

    def test_user_can_list_his_creds(self):
        create_user_and_login(client, "user", "user", "user")
        uuid = jpost(client, "/api/credentials", {
            "label": "Secret1",
            "type": "Generic",
            "value": "Test Value 1234"
        }).json()['uuid']

        uuid2 = jpost(client, "/api/credentials", {
            "label": "Secret2",
            "type": "Github",
            "value": "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"
        }).json()['uuid']

        res = jget(client, "/api/credentials").json()
        self.assertEqual(res['count'], 2)
        items = [
            {'label': 'Secret1', 'type': 'Generic', 'uuid': uuid, 'allow_sync': True},
            {'label': 'Secret2', 'type': 'Github', 'uuid': uuid2, 'allow_sync': True}
        ]
        self.assertEqual(items, res['items'])

        res = jget(client, "/api/credentials?type=Generic").json()
        self.assertEqual(res['count'], 1)
        items = [
            {'label': 'Secret1', 'type': 'Generic', 'uuid': uuid, 'allow_sync': True}
        ]
        self.assertEqual(items, res['items'])

        res = jget(client, "/api/credentials?type=Generic&type=Github").json()
        self.assertEqual(res['count'], 2)
        items = [
            {'label': 'Secret1', 'type': 'Generic', 'uuid': uuid, 'allow_sync': True},
            {'label': 'Secret2', 'type': 'Github', 'uuid': uuid2, 'allow_sync': True}
        ]
        self.assertEqual(items, res['items'])
        res = jget(client, "/api/credentials?label=Secret1").json()
        self.assertEqual(res['count'], 1)

        asserts(self, jget(client, "/api/credentials/" + uuid), status=200, json={
            "label": "Secret1",
            "type": "Generic",
            "uuid": uuid,
            'value': 'Test Value 1234',
            'allow_sync': True
        })
        asserts(self, jget(client, "/api/credentials/" + uuid), status=200, json={
            "label": "Secret1",
            "type": "Generic",
            "uuid": uuid,
            'value': 'Test Value 1234',
            'allow_sync': True
        })
        asserts(self, jget(client, "/api/credentials/" + str(uuid4())), status=404)

    def test_user_cannot_list_others_creds(self):
        create_user_and_login(client, "user", "user", "user")

        uuid = jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Generic",
            "value": "Test Value 1234"
        }).json()['uuid']

        logout(client)

        create_user_and_login(client, "user2", "user2", "user2")

        jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Generic",
            "value": "Test Value 1234"
        })

        response = jget(client, "/api/credentials")

        for item in response.json()['items']:
            self.assertNotEqual(item['uuid'], uuid)

    def test_user_can_modify_his_creds(self):
        create_user_and_login(client, "user", "user", "user")

        cred = jpost(client, "/api/credentials", {
            "label": "Github",
            "type": "Generic",
            "value": "Test Value 1234"
        }).json()

        asserts(self, jput(client, "/api/credentials/Fake", {
                "label": "Github",
                "value": "Test Value 1234"
                }), status=422)
        new_cred = {
            "label": "Changed Label",
            "value": "Changed Value"
        }
        asserts(self, jput(client, "/api/credentials/" + cred['uuid'], {"label": "Changed Label Without Value"}), status=200)

        asserts(self, jput(client, "/api/credentials/" + cred['uuid'], new_cred), status=200)

        asserts(self, jput(client, "/api/credentials/" + str(uuid4()), new_cred), status=404)

        del new_cred['value']
        new_cred['allow_sync'] = True
        new_cred['uuid'] = cred['uuid']
        new_cred['type'] = "Generic"
        asserts(self, jget(client, "/api/credentials"), json={"items": [new_cred], "count": 1})

    def test_invalid_credential(self):
        create_user("user", "user", "user")

        login(client, "user", "user")

        asserts(self, jpost(client, "/api/credentials", {
            "label": "PublicGit",
            "type": "PublicGit",
            "value": "dummy_value"
        }), status=422)

    def test_user_can_access_remotes(self):
        user = create_user("admin", "admin@test.com", "password")
        login(client, "admin", "password")
        asserts(self, jget(client, '/api/credentials/{}/repositories'.format(uuid4())), status=404)
        cred = Credential(label="Github", type="Github", raw_value="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", owner=user)
        cred.save()

        result = asserts(self, jget(client, '/api/credentials/{}/repositories'.format(cred.uuid)), status=200).json()
        self.assertEqual(result[0]['full_name'].startswith("zenscanner/"), True)
        result2 = asserts(self, jget(client, '/api/credentials/{}/repositories?page=2'.format(cred.uuid)), status=200).json()
        self.assertNotEqual(result, result2)

        cred = Credential(label="Generic", type="Generic", raw_value="aaa", owner=user)
        cred.save()

        asserts(self, jget(client, '/api/credentials/{}/repositories'.format(cred.uuid)), status=404)
