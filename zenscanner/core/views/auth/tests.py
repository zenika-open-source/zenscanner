from django.test import TestCase, Client, override_settings
from core.tests.utils import asserts, create_admin_and_login, jget, login, create_user, logout, create_admin, register
from core.models import User
from django.db import transaction
import base64

client = Client()


@override_settings(REGISTRATION_ENABLED=True)
class MeViewTestCase(TestCase):

    def test_user_can_access_me(self):
        asserts(self, login(client, "user", "user"), status=401)
        create_admin_and_login(client, "admin", "admin@test.com", "password")
        asserts(self, jget(client, "/api/auth/me"), status=200,
                json_contains={"username": "admin"}
                )

    def test_user_can_logout(self):
        create_user("user", "user", "user")
        login(client, "user", "user")
        asserts(self, client.get("/api/auth/me"), status=200)
        asserts(self, logout(client), status=200)
        asserts(self, client.get("/api/auth/me"), status=401)

    def test_user_can_login(self):
        asserts(self, login(client, "user", "user"), status=401)
        create_user("user", "user", "user")
        asserts(self, login(client, "user", "user"), status=200)
        asserts(self, login(client, "admin", "admin"), status=401)
        create_admin("admin", "admin", "admin")
        asserts(self, login(client, "admin", "admin"), status=200)

    def test_user_can_login_with_basic_auth(self):
        create_admin("admin", "admin", "admin")
        credentials = base64.b64encode(("admin" + ':' + "admin").encode())
        client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials.decode()
        asserts(self, client.get("/api/auth/me"), status=200,
                json_contains={"username": "admin"}
                )

    def test_user_can_register(self):
        asserts(self, register(client, 'user', 'user', 'user@localhost', 'user'), status=200)

    def test_user_cannot_register_twice(self):
        '''
        This test ensure that when you create a user twice the db count is 1 and not 2
        '''
        self.assertEqual(User.objects.count(), 0)
        create_user("user", "user@localhost", "user")
        self.assertEqual(User.objects.count(), 1)
        with transaction.atomic():
            asserts(self, register(client, 'user', 'user', 'user@localhost', 'user'), status=200)
        self.assertEqual(User.objects.count(), 1)

    def test_user_cannot_register_with_wrong_confirmation(self):
        asserts(self, register(client, 'user', 'user', 'user@localhost', 'resu'), status=422)

    def test_user_can_login_after_register(self):
        asserts(self, register(client, 'user', 'user', 'user@localhost', 'user'), status=200)
        asserts(self, login(client, 'user', 'user'), status=200)

    def test_user_cant_register_with_bad_address(self):
        asserts(self, register(client, 'user', 'user', 'userlocalhost', 'user'), status=422, json={'message': 'Email is not valid'})
        asserts(self, login(client, 'user', 'user'), status=401)

    @override_settings(REGISTRATION_ENABLED=False)
    def test_user_cant_register_with_registration_disabled(self):
        asserts(self, register(client, 'user', 'user', 'user@localhost', 'user'), status=403, json={'message': 'User registration disabled.'})
        asserts(self, login(client, 'user', 'user'), status=401)

    @override_settings(REGISTRATION_DOMAINS=['zenika.com'])
    def test_registration_can_filter_user_email(self):
        asserts(self, register(client, 'user', 'user', 'user@localhost', 'user'), status=403, json={'message': 'Domain not allowed'})
        asserts(self, login(client, 'user', 'user'), status=401)
        asserts(self, register(client, 'user', 'user', 'user@zenika.com', 'user'), status=200)
        asserts(self, login(client, 'user', 'user'), status=200)
