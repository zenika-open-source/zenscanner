from django.test import TestCase, Client
from core.tests.utils import create_user, login, jget
from core.models import Repository, User
from core.utils.paginator import Paginator

client = Client()


class PaginatorTestCase(TestCase):

    def setUp(self):
        user = create_user("user", "user@zenscanner.test", "user")
        for i in range(25):
            Repository(name="{}".format(str(i + 10)[::-1]), url='https://repo{}.zenscanner'.format(i), owner=user).save()

    def test_perpage(self):
        user = User.objects.get(email="user@zenscanner.test")
        self.assertEqual(len(Paginator(Repository).paginate({"per_page": 5})), 5)
        self.assertEqual(len(Paginator(Repository.objects.filter(owner=user)).paginate({"per_page": 5})), 5)
        self.assertEqual(len(Paginator(Repository.objects.filter(owner=user)).paginate({})), 10)

    def test_perpage_invalid_number(self):
        self.assertEqual(len(Paginator(Repository).paginate({"per_page": -1})), 10)

    def test_perpage_zero_value(self):
        p = Paginator(Repository)
        p.paginate({"per_page": 0})
        self.assertEqual(p.count, 25)

    def test_perpage_bad_value(self):
        p = Paginator(Repository)
        page = p.paginate({"per_page": "a"})
        self.assertEqual(len(page), 10)

    def test_pagenum(self):
        user = User.objects.get(email="user@zenscanner.test")
        self.assertEqual(len(Paginator(Repository).paginate({"page": 50})), 0)
        self.assertEqual(len(Paginator(Repository.objects.filter(owner=user)).paginate({"page": 1})), 10)
        self.assertEqual(len(Paginator(Repository.objects.filter(owner=user)).paginate({})), 10)
        self.assertEqual(len(Paginator(Repository).paginate({"page": 3})), 5)

    def test_order(self):
        name_ascending = Paginator(Repository).paginate({"order_by": "name", "ascending": True})
        self.assertEqual(name_ascending[0].name, "01")
        self.assertEqual(name_ascending[1].name, "02")
        name_not_ascending = Paginator(Repository).paginate({"order_by": "name", "ascending": False})
        self.assertEqual(name_not_ascending[0].name, "92")
        self.assertEqual(name_not_ascending[1].name, "91")
        url_ascending = Paginator(Repository).paginate({"order_by": "url", "ascending": True})
        self.assertEqual(url_ascending[0].url, "https://repo0.zenscanner")
        self.assertEqual(url_ascending[1].url, "https://repo1.zenscanner")
        p = Paginator(Repository)
        url_not_ascending = p.paginate({"order_by": "url", "ascending": False})
        self.assertEqual(url_not_ascending[0].url, "https://repo9.zenscanner")
        self.assertEqual(url_not_ascending[1].url, "https://repo8.zenscanner")
        self.assertEqual(len(url_not_ascending), 10)
        self.assertEqual(p.count, 25)

    def test_repo_search(self):
        login(client, "user", "user")
        get = jget(client, "/api/repositories?search=repo1&limit=5&page=2&order_by=url&ascending=0")
        self.assertEqual(11, get.json()['count'])
        self.assertEqual(5, len(get.json()['items']))
        # self.assertEqual("42", get.json()['items'][0]['name']) TODO: Implement data sort in paginate decorator
        # self.assertEqual("https://repo14.zenscanner", get.json()['items'][0]['url'])
