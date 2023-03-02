from functools import wraps
from django.http import JsonResponse
from core.models import User
from django.core.handlers.wsgi import WSGIRequest


def superuser_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        class_mode = (type(request) != WSGIRequest)
        username = request.user.username if not class_mode else args[0].user.username
        user = User.objects.get(username=username)
        if user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return JsonResponse({'message': "Unauthorized"}, status=401)
    return wrap


def login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        class_mode = (type(request) != WSGIRequest)
        is_anon = request.user.is_anonymous if not class_mode else args[0].user.is_anonymous
        if is_anon:
            return JsonResponse({'message': "Unauthorized"}, status=401)
        else:
            return function(request, *args, **kwargs)
    return wrap


def worker_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        class_mode = (type(request) != WSGIRequest)
        is_worker_connected = hasattr(request, 'worker') if not class_mode else hasattr(args[0], 'worker')
        if not is_worker_connected:
            return JsonResponse({'message': "Unauthorized"}, status=401)
        else:
            return function(request, *args, **kwargs)
    return wrap


def all_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        class_mode = (type(request) != WSGIRequest)
        is_anon = request.user.is_anonymous if not class_mode else args[0].user.is_anonymous
        is_worker_connected = hasattr(request, 'worker') if not class_mode else hasattr(args[0], 'worker')
        is_repository_connected = hasattr(request, 'repository') if not class_mode else hasattr(args[0], 'repository')
        if is_anon and not is_worker_connected and not is_repository_connected:
            return JsonResponse({'message': "Unauthorized"}, status=401)
        else:
            return function(request, *args, **kwargs)
    return wrap
