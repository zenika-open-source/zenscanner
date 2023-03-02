from django.urls import path
from ninja import NinjaAPI
from django.core.exceptions import ObjectDoesNotExist

from core.views import (
    auth,
    repositories,
    access_tokens,
    credentials,
    scans,
    vulnerabilities,
    workers,
    root
)

api = NinjaAPI(
    title="ZenScanner",
    version="0.1.0",
    description="ZenScanner is a no CI DevSecOps tool."
)


@api.exception_handler(ObjectDoesNotExist)
def object_not_found(request, exc):
    return api.create_response(
        request,
        {"message": "Not found"},
        status=404,
    )


api.add_router('/access_tokens', access_tokens.router)
api.add_router('/auth', auth.router)
api.add_router('/credentials', credentials.router)
api.add_router('/repositories', repositories.router)
api.add_router('/scans', scans.router)
api.add_router('/', root.router)
api.add_router('/vulnerabilities', vulnerabilities.router)
api.add_router('/workers', workers.router)

urlpatterns = [
    path("api/", api.urls),
]
