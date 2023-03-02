from core.utils.security import AuthBearer, BasicAuth
from ninja.pagination import paginate
from ninja import Router, Query
from core.models import Vulnerability
from .schemas import (
    VulnerabilitySchema,
    VulnerabilityFilters
)
from uuid import UUID
from typing import List
from datetime import datetime, timedelta
import json

router = Router(tags=["Vulnerabilities"], auth=[AuthBearer(), BasicAuth()])


@router.get('/{vulnerability_uuid}', response=VulnerabilitySchema, exclude_none=True)
def get_vulnerability(request, vulnerability_uuid: UUID):

    vuln = Vulnerability.objects.get(
        uuid=vulnerability_uuid,
        scan__repository__owner=request.user
    )

    return vuln


@router.get('/{vulnerability_uuid}/sarif')
def get_vulnerability_sarif(request, vulnerability_uuid: UUID):

    vuln = Vulnerability.objects.get(
        uuid=vulnerability_uuid,
        scan__repository__owner=request.user
    )

    return json.loads(vuln.sarif)


@router.get('', response=List[VulnerabilitySchema], exclude_none=True)
@paginate
def list_scans(request, filters: VulnerabilityFilters = Query(...)):
    vs = Vulnerability.objects.filter(scan__repository__owner=request.user)

    if filters.tool:
        vs = vs.filter(tool__in=filters.tool)
    if filters.level:
        vs = vs.filter(level__in=filters.level)
    if filters.details:
        vs = vs.filter(details__contains=filters.details)
    if filters.author_email:
        vs = vs.filter(author_email__contains=filters.author_email)
    if filters.path:
        vs = vs.filter(path__contains=filters.path)
    if filters.rule:
        vs = vs.filter(rule__contains=filters.rule)
    if filters.scan:
        vs = vs.filter(scan__uuid=filters.scan)
    if filters.new is not None:
        vs = vs.filter(is_new=filters.new)
    if filters.days:

        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        vs = vs.filter(created_at__gte=(today - timedelta(days=filters.days - 1)))

    return vs
