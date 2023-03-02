from django.test import TestCase, Client
from core.tests.utils import jget, asserts
from core.tests.utils import create_user_and_login

client = Client()


class TypesViewTestCase(TestCase):

    def test_view_all(self):
        asserts(self, jget(client, "/api/types/all"), status=401, json=[])
        create_user_and_login(client, "user", "user", "user")
        asserts(self, jget(client, "/api/types/undefined"), status=404, json=[])
        res = jget(client, "/api/types/all").json()
        self.assertEqual(res['credentials']['total_count'], 2)
        for value in ["Github", "Generic"]:
            self.assertEqual(value in res['credentials']['items'], True)
        self.assertEqual(res['scanners']['total_count'], 4)
        for value in ["Gitleaks", "Bandit", "Trivy", "Semgrep"]:
            self.assertEqual(value in res['scanners']['items'], True)
        self.assertEqual(res['pullers']['total_count'], 4)
        for value in ["Github", "Uploaded", "NoCreds", "NoCredsSvn"]:
            self.assertEqual(value in res['pullers']['items'], True)

    def test_view_credentials(self):
        create_user_and_login(client, "user", "user", "user")
        res = jget(client, "/api/types/credentials").json()
        self.assertEqual(res['total_count'], 2)
        for value in ["Github", "Generic"]:
            self.assertEqual(value in res['items'], True)

    def test_view_scanners(self):
        create_user_and_login(client, "user", "user", "user")
        res = jget(client, "/api/types/scanners").json()
        self.assertEqual(res['total_count'], 4)
        for value in ["Gitleaks", "Bandit", "Trivy", "Semgrep"]:
            self.assertEqual(value in res['items'], True)

    def test_view_pullers(self):
        create_user_and_login(client, "user", "user", "user")
        res = jget(client, "/api/types/pullers").json()
        self.assertEqual(res['total_count'], 4)
        for value in ["Github", "Uploaded", "NoCreds", "NoCredsSvn"]:
            self.assertEqual(value in res['items'], True)
