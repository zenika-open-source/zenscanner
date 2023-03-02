from ninja import ModelSchema, Field, Schema
from uuid import UUID
from typing import List
from core.models import Repository


class RepositorySchema(ModelSchema):
    credential: UUID | str = Field(..., alias="credential.uuid")
    branches: None | List[str] = Field(..., alias="branches")

    class Config:
        model = Repository
        model_exclude = ['id', 'owner']


class CreateRepository(Schema):
    name: str
    url: str
    credential: UUID | None
    source_control: str = "git"


class UpdateRepository(Schema):
    credential: UUID | None | str
    name: str | None
    url: str | None


class RepositoryFilters(Schema):
    search: str | None


class RepositoryScansFilters(Schema):
    branch: str | None
    last_commit: str | None
    level: List[int] | None
