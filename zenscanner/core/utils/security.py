from ninja.security import APIKeyHeader, HttpBearer, HttpBasicAuth
from core.models import Repository, WorkerToken, User, AccessToken, UserSession
from django.core.exceptions import ObjectDoesNotExist
import jwt
from django.conf import settings


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = User.objects.get(username=username)
        if user.is_good_password(password):
            request.user = user
            return user


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if len(token) == 36:
            try:
                access_token = AccessToken.objects.get(token=token)
                if access_token.is_valid():
                    request.user = access_token.owner
                    return request.user
                else:
                    access_token.delete()
            except Exception:
                pass
        else:
            try:
                infos = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                sub = infos.get('sub', None)
                session = infos.get('jti', None)
                s = UserSession.objects.select_related().get(id=session, user=sub)
                request.session = s
                request.user = s.user
                return request
            except Exception:
                pass


class RepositoryAuthKey(APIKeyHeader):
    param_name = "Repository"

    def authenticate(self, request, key):
        try:
            repo = Repository.objects.get(authkey=key)
            if repo:
                request.repository = repo
                return repo
        except Exception:
            pass


class WorkerAuthKey(APIKeyHeader):
    param_name = "Worker"

    def authenticate(self, request, key):
        try:
            worker_token = WorkerToken.objects.get(token=key)
            if worker_token.is_valid():
                request.worker = worker_token
                request.worker.repository = request.worker.scan.repository
                return worker_token
        except ObjectDoesNotExist:
            return False
