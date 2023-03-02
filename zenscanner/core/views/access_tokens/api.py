from ninja import Router, Schema, ModelSchema, Field
from uuid import UUID
from core.models import AccessToken
from core.utils.security import AuthBearer, BasicAuth
from ninja.pagination import paginate
from typing import List
from datetime import datetime

router = Router(tags=["Access Tokens"], auth=[AuthBearer(), BasicAuth()])


class AccessTokenSchema(ModelSchema):
    class Config:
        model = AccessToken
        model_exclude = ['owner']


class CreateAccessToken(Schema):
    label: str = Field(..., min_length=1)
    expire: datetime | None


@router.get('', response=List[AccessTokenSchema])
@paginate
def list_access_tokens(request, label: str = None, token: str = None):
    at = AccessToken.objects.filter(owner=request.user)
    if label:
        at = at.filter(label__contains=label)
    if token:
        at = at.filter(token__contains=token)
    return at


@router.post('', response=AccessTokenSchema)
def create_access_token(request, data: CreateAccessToken):

    access_token = AccessToken(label=data.label, owner=request.user)
    if data.expire:
        access_token.expire = data.expire
    access_token.save()
    return access_token


@router.delete('/{token}')
def delete_access_token(request, token: UUID):
    AccessToken.objects.get(owner=request.user, token=token).delete()
    return {}
