from core.utils.security import AuthBearer, BasicAuth
from ninja.pagination import paginate
from ninja import Router, Query
from uuid import UUID
from typing import List
from core.models import Scan, ScanResult
from .schemas import (
    ScanResultSchema,
    ScanSchemaWithRepository,
    ScanFilters
)
from datetime import datetime, timedelta
from core.utils.security import RepositoryAuthKey
from django.db.models import Q
import json

router = Router(tags=["Scans"], auth=[AuthBearer(), BasicAuth()])


def get_scan_for_request(request, scan_uuid):
    if hasattr(request, 'repository'):
        return Scan.objects.get(repository=request.repository, uuid=scan_uuid)
    else:
        return Scan.objects.get(repository__owner=request.user, uuid=scan_uuid)


@router.get('/{scan_uuid}/result', response=ScanResultSchema, auth=[AuthBearer(), BasicAuth(), RepositoryAuthKey()])
def get_scan_result(request, scan_uuid: UUID):
    scan = get_scan_for_request(request, scan_uuid)
    scan.update_vulnerability_count()  # TODO: Fix update need
    return scan


@router.get('', response=List[ScanSchemaWithRepository])
@paginate
def list_scans(request, filters: ScanFilters = Query(...)):
    scans = Scan.objects.filter(repository__owner=request.user)

    if filters.status:
        scans = scans.filter(Q(_status__in=filters.status))

    if filters.days:

        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        scans = scans.filter(created_at__gte=(today - timedelta(days=filters.days - 1)))

    return scans


@router.get('/{scan_uuid}', response=ScanSchemaWithRepository, auth=[AuthBearer(), BasicAuth(), RepositoryAuthKey()])
def get_scan(request, scan_uuid: UUID):
    scan = get_scan_for_request(request, scan_uuid)

    scan.update_vulnerability_count()  # TODO: Fix update need
    return scan


@router.get('/{scan_uuid}/sarif', auth=[AuthBearer(), BasicAuth(), RepositoryAuthKey()])
def get_scan_sarif(request, scan_uuid: UUID):
    scan = get_scan_for_request(request, scan_uuid)
    sr = ScanResult.objects.get(task_id=scan.uuid)
    return json.loads(sr.sarif)
