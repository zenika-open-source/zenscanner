from core.models import Scan, Vulnerability
from ninja import ModelSchema, Schema, Field
from uuid import UUID
from typing import List
from pydantic import conint


class Task(Schema):
    task_id: UUID


class ScanRepository(Schema):
    branch: str | None


class MatchedScanners(Schema):
    old: List[str]
    new: List[str]


class ScanSchema(ModelSchema):
    status: str = Field(..., alias="status")
    branch_url: str = Field(..., alias="branch_url")
    commit_url: str = Field(..., alias="commit_url")
    scanners: List[str] = Field(..., alias="scanners")
    matched_scanners: MatchedScanners = Field(..., alias="matched_scanners")

    class Config:
        model = Scan
        model_exclude = ['repository']


class ScanSchemaWithRepository(ScanSchema):
    from core.views.repositories.schemas import RepositorySchema
    repository: RepositorySchema = Field(..., alias="repository")


class VulnerabilitySchema(ModelSchema):
    from core.views.repositories.schemas import RepositorySchema
    repository: RepositorySchema = Field(..., alias="scan.repository")

    class Config:
        model = Vulnerability
        model_exclude = ['sarif', 'repository', 'scan']


class ScanResultSchema(ScanSchema):
    vulnerabilities: List[VulnerabilitySchema] = Field(..., alias="vulnerability_set")


class ScanFilters(Schema):
    days: conint(ge=0) | None
    status: List[str] | None
