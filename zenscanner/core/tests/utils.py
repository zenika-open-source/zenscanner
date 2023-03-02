from core.models import User
import json
from requests.models import Response
import requests
from django.test import TestCase, override_settings

"""
from django.db import connection
from django.test.utils import CaptureQueriesContext
with CaptureQueriesContext(connection):
    for query in connection.queries:
        print(query)
"""


def jget(client, url):
    return client.get(url)


def jpost(client, url, params={}):
    return client.post(url, json.dumps(params), content_type="application/json")


def jput(client, url, params):
    return client.put(url, json.dumps(params), content_type="application/json")


def jdelete(client, url, params={}):
    return client.delete(url, json.dumps(params), content_type="application/json")


def asserts(test, response, **kwargs):
    if kwargs.get("status"):
        test.assertEqual(response.status_code, kwargs.get("status"))
    if kwargs.get("contains"):
        test.assertContains(response, kwargs.get("contains"))
    if kwargs.get("json"):
        test.assertEqual(response.json(), kwargs.get("json"))
    if kwargs.get("json_contains"):
        for attr, value in kwargs.get("json_contains").items():
            test.assertEqual(response.json()[attr], value)
    return response


def create_admin(username, email, password):
    return User.objects.create_superuser(username, email, password)


def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user


def login(client, username, password):
    res = jpost(client, "/api/auth/login", {
        'username': username,
        'password': password,
    })

    if res.json().get('access_token', None):
        client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + res.json().get('access_token')
    return res


def logout(client):
    return jget(client, "/api/auth/logout")


def register(client, username, password, email, confirmation):
    params = {
        "username": username,
        "password": password,
        "email": email,
        "passwordConfirmation": confirmation,
    }
    return jpost(client, "/api/auth/register", params=params)


def create_admin_and_login(client, username, email, password):
    create_admin(username, email, password)
    return login(client, username, password)


def create_user_and_login(client, username, email, password):
    create_user(username, email, password)
    return login(client, username, password)


@override_settings(CELERY_BROKER_URL='memory://')
@override_settings(CELERY_RESULT_BACKEND='cache')
@override_settings(CELERY_CACHE_BACKEND='memory')
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@override_settings(USE_TZ=True)
@override_settings(API_URL="http://testserver")
class TaskTestCase(TestCase):
    pass


class MockedResponse():

    def __init__(self, **kwargs):
        self.status_code = 200
        if "content" in kwargs:
            self.content = kwargs['content']


class RequestMockPatcher:

    def __init__(self, client, api_url):
        self.client = client
        self.api_url = api_url
        self.backup_defaults()

    def backup_defaults(self):
        self.client_default = self.client.defaults

    def restore_defaults(self):
        self.client.defaults = self.client_default

    def set_client_default(self, kwargs):
        self.backup_defaults()
        if kwargs.get('headers', None):
            headers = kwargs.get('headers')
            for header in headers:
                self.client.defaults['HTTP_' + header.upper()] = headers[header]

    def django_to_response(self, response):
        rr = Response()
        rr._content = response.content
        rr.status_code = response.status_code
        rr.cookies = response.cookies
        rr.headers = response.headers
        return rr

    def get_client_url(self, url):
        return url.replace(self.api_url, "")

    def mock_delete(self, *args, original_requests=requests.delete, **kwargs):
        if args[0].startswith(self.api_url):
            self.set_client_default(kwargs)
            response = self.client.delete(self.get_client_url(args[0]))
            self.restore_defaults()
            return self.django_to_response(response)
        return original_requests(*args, **kwargs)

    def mock_get(self, *args, original_requests=requests.get, **kwargs):
        if args[0].startswith(self.api_url):
            self.set_client_default(kwargs)
            response = self.client.get(self.get_client_url(args[0]))
            self.restore_defaults()
            return self.django_to_response(response)
        elif args[0].startswith("http://mockeds3"):
            filename = args[0].split('/')[-1]
            path = args[0].split('/')[3]
            with open("/tmp/{}/{}".format(path, filename), "rb") as uploaded:
                return MockedResponse(content=uploaded.read())
        return original_requests(*args, **kwargs)

    def mock_post(self, *args, original_requests=requests.post, **kwargs):
        if args[0].startswith(self.api_url):
            self.set_client_default(kwargs)
            if 'json' in kwargs:
                response = self.client.post(self.get_client_url(args[0]), data=kwargs.get('json'), content_type="application/json")
            else:
                response = self.client.post(self.get_client_url(args[0]), data=kwargs.get('data'))
            self.restore_defaults()
            return self.django_to_response(response)
        return original_requests(*args, **kwargs)

    def mock_put(self, *args, original_requests=requests.put, **kwargs):
        if args[0].startswith(self.api_url):
            self.set_client_default(kwargs)
            if 'json' in kwargs:
                response = self.client.put(self.get_client_url(args[0]), data=kwargs.get('json'), content_type="application/json")
            else:
                response = self.client.put(self.get_client_url(args[0]), data=kwargs.get('data'))
            self.restore_defaults()
            return self.django_to_response(response)
        elif args[0].startswith("http://mockeds3"):
            filename = args[0].split('/')[-1]
            path = args[0].split('/')[3]
            with open("/tmp/{}/{}".format(path, filename), "wb") as uploaded:
                uploaded.write(kwargs.get('data').read())
            return MockedResponse()
        return original_requests(*args, **kwargs)
