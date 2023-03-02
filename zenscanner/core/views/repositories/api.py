from ninja import Router, Query
from uuid import UUID
from core.models import Repository, Credential, Scan, WorkerToken
from core.utils.security import AuthBearer, BasicAuth
from ninja.pagination import paginate
from typing import List
from .utils import RemoteUpload, RepositoryUploadInformation, TaskId
from core.celery import run_scan
from django.db.models import Q
from core.utils.security import RepositoryAuthKey
from .schemas import (
    RepositorySchema,
    CreateRepository,
    UpdateRepository,
    RepositoryFilters,
    RepositoryScansFilters,
)

from core.views.scans.schemas import (
    ScanSchema,
    ScanRepository,
    Task
)

router = Router(tags=["Repositories"], auth=[AuthBearer(), BasicAuth()])


@router.get('', response=List[RepositorySchema])
@paginate
def list_repositories(request, filters: RepositoryFilters = Query(...)):
    repos = Repository.objects.filter(owner=request.user)
    if filters.search:
        repos = repos.filter(Q(name__contains=filters.search) | Q(url__contains=filters.search))
    return repos


@router.get('/{repository_uuid}', response=RepositorySchema)
def get_repository(request, repository_uuid: UUID, refresh_branches: str = None):
    repository = Repository.objects.get(owner=request.user, uuid=repository_uuid)
    if refresh_branches is not None:
        repository.update_branches()
    return repository


@router.delete('/{repository_uuid}')
def delete_repository(request, repository_uuid: UUID):
    Repository.objects.get(owner=request.user, uuid=repository_uuid).delete()
    return {}


@router.put('/{repository_uuid}', response=RepositorySchema)
def update_repository(request, repository_uuid: UUID, data: UpdateRepository):
    repo = Repository.objects.get(owner=request.user, uuid=repository_uuid)

    if data.name:
        repo.name = data.name
    if data.url:
        repo.url = data.name
    if data.credential == "":
        repo.credential = None
    elif type(data.credential == UUID):
        repo.credential = Credential.objects.get(_uuid=data.credential)
    repo.save()
    return Repository.objects.get(owner=request.user, uuid=repository_uuid)


@router.post('', response=RepositorySchema)
def create_repository(request, data: CreateRepository):
    if data.credential:
        cred = Credential.objects.get(owner=request.user, _uuid=data.credential)
    else:
        cred = None
    repo = Repository(owner=request.user, name=data.name, url=data.url, credential=cred, source_control=data.source_control)
    repo.save()
    return repo


@router.get('/{repository_uuid}/upload', response=RepositoryUploadInformation, auth=[RepositoryAuthKey(), AuthBearer(), BasicAuth()])
def get_repository_upload_information(request, repository_uuid: UUID):
    if hasattr(request, 'repository'):
        repository = request.repository
    else:
        repository = Repository.objects.get(owner=request.user, uuid=repository_uuid)
    return RemoteUpload(repository).get_link(request)


@router.put('/{repository_uuid}/upload', response=TaskId, auth=[RepositoryAuthKey(), AuthBearer(), BasicAuth()])
def upload_repository_source(request, repository_uuid: UUID):
    if hasattr(request, 'repository'):
        repository = request.repository
    else:
        repository = Repository.objects.get(owner=request.user, uuid=repository_uuid)
    return RemoteUpload(repository).upload(request)


@router.post('/{repository_uuid}/scan', response=Task)
def start_scan(request, repository_uuid: UUID, data: ScanRepository):
    repo = Repository.objects.get(owner=request.user, uuid=repository_uuid)
    scan = Scan(repository=repo)
    if data.branch:
        scan.branch = data.branch
        kwargs = {'branch': data.branch}
    else:
        kwargs = {}
    scan.save()
    worker_token = WorkerToken(scan=scan)
    worker_token.save()
    task = run_scan.apply_async(args=[worker_token.token], kwargs=kwargs, task_id=str(scan.uuid))
    return {"task_id": task.id}


@router.get('/{repository_uuid}/scans', response=List[ScanSchema])
@paginate
def list_repository_scans(request, repository_uuid: UUID, filters: RepositoryScansFilters = Query(...)):
    repo = Repository.objects.get(owner=request.user, uuid=repository_uuid)
    scans = Scan.objects.filter(repository=repo)

    if filters.branch:
        scans = scans.filter(branch__contains=filters.branch)

    if filters.last_commit:
        scans = scans.filter(last_commit__contains=filters.last_commit)

    if filters.level:
        filter = Q()
        if 0 in filters.level:
            filter = (filter | Q(none_count__gt=0))
        if 1 in filters.level:
            filter = (filter | Q(note_count__gt=0))
        if 2 in filters.level:
            filter = (filter | Q(warning_count__gt=0))
        if 3 in filters.level:
            filter = (filter | Q(error_count__gt=0))
        if filter != Q():
            scans = scans.filter(filter)

    return scans
