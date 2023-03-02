from ninja import Router, Schema, Query
from uuid import UUID
from core.models import Credential
from ninja.errors import HttpError
from core.utils.security import AuthBearer, BasicAuth
from ninja.pagination import paginate
from typing import List
from django.db.models import Q
from .schemas import (
    CredentialSchema,
    CredentialFilters,
    CredentialWithValueSchema,
    RemoteRepository,
    CreateCredential,
    UpdateCredential
)

router = Router(tags=["Credentials"], auth=[AuthBearer(), BasicAuth()])


class Message(Schema):
    message: str


@router.get('', response=List[CredentialSchema])
@paginate
def list_credentials(request, filters: CredentialFilters = Query(...)):
    creds = Credential.objects.filter(owner=request.user)
    if filters.type:
        creds = creds.filter(Q(type__in=filters.type))
    if filters.label:
        creds = creds.filter(Q(label__contains=filters.label))
    return creds


@router.get('/{credential_uuid}', response=CredentialWithValueSchema)
def get_credential(request, credential_uuid: UUID):
    return Credential.objects.get(_uuid=credential_uuid, owner=request.user)


@router.get(
    '/{credential_uuid}/repositories',
    response=List[RemoteRepository],
    description="Lists tes repositories accessible with this credential. The attribute `can_sync` of credential plugin must be `True`"
)
def list_credential_repositories(request, credential_uuid: UUID, page: int = 1):
    cred = Credential.objects.get(_uuid=credential_uuid, owner=request.user)
    instance = cred.get_instance()
    if hasattr(instance, 'can_sync') and instance.can_sync:
        return cred.get_instance().list(page=page)
    else:
        raise HttpError(404, "Not Found")

    return cred


@router.post('', response={200: CredentialSchema, 422: Message})
def create_credential(request, data: CreateCredential):
    try:
        cred = Credential(label=data.label, owner=request.user, raw_value=data.value, type=data.type)
        cred.save()
        return cred
    except KeyError:
        return 422, {'message': 'Unprocessable Entity'}


@router.delete('/{credential_uuid}')
def delete_credential(request, credential_uuid: UUID):
    Credential.objects.get(owner=request.user, _uuid=credential_uuid).delete()
    return {}


@router.put('/{credential_uuid}', response={200: CredentialSchema, 422: Message, 404: Message})
def update_credential(request, credential_uuid: UUID, data: UpdateCredential):
    cred = Credential.objects.get(_uuid=credential_uuid, owner=request.user)
    cred.label = data.label
    if data.value:
        cred.raw_value = data.value
    cred.save()
    return cred
