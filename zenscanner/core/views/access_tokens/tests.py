from django.test import TestCase, Client
from core.tests.utils import create_user_and_login, asserts, jpost, jdelete, jget, logout
import uuid
from datetime import datetime, timedelta
from core.models import AccessToken
from django.utils.timezone import make_aware

client = Client()


class AccessTokenViewTestCase(TestCase):

    def test_user_can_manage_token(self):
        create_user_and_login(client, "user", "user", "user")
        asserts(self, jpost(client, "/api/access_tokens",
                            {'label': "", }), status=422)
        token_generated = asserts(self, jpost(client, "/api/access_tokens", {'label': "View access token1", }), status=200,
                                  json_contains={"label": 'View access token1'}).json()['token']
        asserts(self, jpost(client, "/api/access_tokens", {'label': "View access token2", }), status=200,
                json_contains={"label": 'View access token2'}).json()['token']
        asserts(self, jget(client, "/api/access_tokens"), status=200,
                json_contains={"count": 2})
        asserts(self, jget(client, "/api/access_tokens?label=token1"), status=200,
                json_contains={"count": 1})
        asserts(self, jget(client, "/api/access_tokens?token=" + token_generated), status=200,
                json_contains={"count": 1})
        asserts(self, jget(client, "/api/access_tokens?label=AAAA&token=AAA"), status=200,
                json_contains={"count": 0})
        asserts(self, jdelete(client, "/api/access_tokens/" + str(uuid.uuid4())), status=404)
        asserts(self, jdelete(client, "/api/access_tokens/" + token_generated), status=200)

    def test_user1_can_not_delete_user2_token(self):
        create_user_and_login(client, "user", "user", "user")
        asserts(self, jpost(client, "/api/access_tokens",
                            {'label': "View access token", }), status=200, json_contains={"label": 'View access token'})
        token_generated = asserts(self, jget(
            client, "/api/access_tokens"), status=200).json()['items'][0]['token']
        logout(client)

        create_user_and_login(client, "user2", "user2", "user2")
        asserts(self, jdelete(client, "/api/access_tokens/" + token_generated), status=404)

    def test_server_generate_different_tokens(self):
        create_user_and_login(client, "user", "user", "user")
        asserts(self, jpost(client, "/api/access_tokens",
                            {'label': "Token 0", }), status=200)
        asserts(self, jpost(client, "/api/access_tokens",
                            {'label': "Token 1", }), status=200)
        response = client.get("/api/access_tokens")
        token_0_generated = response.json()['items'][0]['token']
        token_1_generated = response.json()['items'][1]['token']
        self.assertNotEqual(token_0_generated, token_1_generated)

    def test_user_can_login_with_access_token(self):
        create_user_and_login(client, "user", "user", "user")
        token_generated = jpost(client, "/api/access_tokens",
                                {'label': "View access token", }).json()['token']
        logout(client)
        client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + 'not an uuid'
        asserts(self, jget(client, "/api/auth/me"), status=401)
        client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + str(uuid.uuid4())
        asserts(self, jget(client, "/api/auth/me"), status=401)
        client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + token_generated
        asserts(self, jget(client, "/api/auth/me"), status=200,
                json_contains={"username": 'user'})

    def test_user_can_expire_access_token(self):
        create_user_and_login(client, "user2", "user2", "user2")
        token_generated = jpost(client, "/api/access_tokens",
                                {'label': "View access token", 'expire': int(datetime.timestamp(datetime.now() + timedelta(days=1)))}).json()['token']
        logout(client)
        client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + token_generated
        asserts(self, jget(client, "/api/auth/me"), status=200, json_contains={"username": 'user2'})
        access_token = AccessToken.objects.get(token=token_generated)
        access_token.deleted_at = make_aware(datetime.now() + timedelta(days=-1))
        access_token.save()
        asserts(self, jget(client, "/api/auth/me"), status=401)
