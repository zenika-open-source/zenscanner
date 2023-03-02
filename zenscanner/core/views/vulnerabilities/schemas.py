from core.models import Vulnerability
from ninja import ModelSchema, Schema, Field
from typing import List, Optional
from uuid import UUID
from pydantic import conint


class RegionSnippet(Schema):
    text: Optional[str]


class Region(Schema):
    snippet: Optional[RegionSnippet]
    startLine: Optional[int]
    startColumn: Optional[int]


class ArtifactLocation(Schema):
    uri: Optional[str]


class PhysicalLocation(Schema):
    region: Optional[Region]
    artifactLocation: Optional[ArtifactLocation]


class Location(Schema):
    physicalLocation: PhysicalLocation


class VulnerabilitySchema(ModelSchema):
    from core.views.repositories.schemas import RepositorySchema
    repository: RepositorySchema = Field(..., alias="scan.repository")
    vulnerability_url: str = Field(..., alias="vulnerability_url")
    commit_url: str = Field(..., alias="commit_url")
    level: int
    locations: List[Location] = Field(..., alias="locations")

    class Config:
        model = Vulnerability
        model_exclude = ['sarif', 'repository', 'scan']


class VulnerabilityFilters(Schema):
    details: str | None
    tool: List[str] | None
    level: List[int] | None
    author_email: str | None
    path: str | None
    rule: str | None
    scan: UUID | None
    new: bool | None
    days: conint(ge=0) | None
