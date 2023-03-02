from ninja import ModelSchema, Schema, Field
from uuid import UUID
from core.models import Credential
from typing import List


class CredentialSchema(ModelSchema):
    uuid: UUID = Field(..., alias="uuid")

    class Config:
        model = Credential
        model_exclude = ['owner']


class CredentialWithValueSchema(ModelSchema):
    uuid: UUID = Field(..., alias="uuid")
    value: str = Field(..., alias="raw_value")

    class Config:
        model = Credential
        model_exclude = ['owner']


class RemoteRepository(Schema):
    url: str
    name: str
    full_name: str


class CreateCredential(Schema):
    label: str = Field(..., min_length=1)
    type: str
    value: str | None


class UpdateCredential(Schema):
    label: str = Field(..., min_length=1)
    value: str | None


class CredentialFilters(Schema):
    type: List[str] = Field(None, alias='type')
    label: str = None
