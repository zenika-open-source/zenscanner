from ninja import Router
from core.views.repositories.schemas import RepositorySchema
from core.views.credentials.schemas import CredentialWithValueSchema
from core.utils.security import WorkerAuthKey
from core.models import WorkerToken, Branch, Vulnerability, ScanResult
import json
from .schemas import ScanInformation
from django.db.models import Q
from django.http import JsonResponse
from core.views.repositories.utils import RemoteUpload
from core.utils.exporters import Exporter

router = Router(tags=["Workers"], auth=WorkerAuthKey())


@router.delete('')
def end_scan(request):
    WorkerToken.objects.get(token=request.worker.token).delete()
    Exporter(worker_token=request.worker).execute()
    scan = request.worker.scan
    scan._status = 'SUCCESS'
    scan.save()
    scan.update_vulnerability_count()


@router.get('/repository', response=RepositorySchema)
def get_worker_repository(request):
    scan = request.worker.scan
    if scan._status != 'RUNNING':
        scan._status = 'RUNNING'
        scan.save()
    return request.worker.repository


@router.get('/repository/credential', response=CredentialWithValueSchema)
def get_worker_credential(request):
    return request.worker.repository.credential


@router.put('/information')
def update_scan_information(request, data: ScanInformation):
    if data.branch:
        request.worker.scan.branch = data.branch
        Branch.objects.get_or_create(repository=request.worker.scan.repository, name=data.branch)
    if data.last_commit:
        request.worker.scan.last_commit = data.last_commit

    request.worker.scan.save()
    return {}


@router.get('/download')
def download_worker_repository_archive(request):
    return RemoteUpload(request.worker.scan.repository).download(request)


def get_vulnerability_level(level: str) -> int:
    level = level.lower()
    if level in ["error", "high"]:
        return 3
    elif level in ["warning", "medium"]:
        return 2
    elif level == ["note", "low"]:
        return 1
    else:
        return 0


@router.put('/result')
def add_worker_result(request):
    try:
        sarif = json.loads(request.body)
        scan = request.worker.scan
        repository = request.worker.scan.repository
        sr = ScanResult.objects.filter(repository=repository, branch=scan.branch, task_id=scan.uuid)
        for run in sarif['runs']:
            for result in run['results']:
                for loc in result.get('locations', []):
                    if len(loc.get('physicalLocation', {}).get('region', {}).get('snippet', {}).get('text', '')) > 100:
                        loc['physicalLocation']['region']['snippet']['text'] = ""
        if not sr:
            sr = ScanResult(
                repository=repository,
                branch=scan.branch,
                sarif=json.dumps(sarif),
                task_id=scan.uuid
            )
            sr.save()
        else:
            sr = sr[0]
            old_sarif = json.loads(sr.sarif)
            for run in sarif['runs']:
                old_sarif['runs'].append(run)
            sr.sarif = json.dumps(old_sarif)
            sr.save()

        last_commit = request.GET.get('last_commit', None)
        if last_commit:
            if sr.last_commit != last_commit:
                sr.last_commit = last_commit
                sr.save()

        for run in sarif.get('runs', []):
            tool_name = run.get('tool', {}).get('driver', {}).get('name', "")
            if run.get('results', []):
                for result in run.get('results', []):
                    old = Vulnerability.objects.filter(
                        ~Q(~Q(scan=scan) & ~Q(repository=repository)),
                        tool=tool_name,
                        rule=result.get('ruleId', ''),
                        path=result.get('locations', [{}])[0].get('physicalLocation', {}).get('artifactLocation', {}).get('uri', "").replace('file:///src', ''),
                        details=result.get('message', {}).get('text', ""),
                        commit_id=result.get('properties', {}).get('commit', ""),
                        author_email=result.get('properties', {}).get('email', ""),
                    ).count()
                    vuln = Vulnerability(
                        scan=scan,
                        repository=repository,
                        tool=tool_name,
                        rule=result.get('ruleId', ''),
                        path=result.get('locations', [{}])[0].get('physicalLocation', {}).get('artifactLocation', {}).get('uri', "").replace('file:///src', ''),
                        details=result.get('message', {}).get('text', ""),
                        level=get_vulnerability_level(result.get('level', '')),
                        sarif=json.dumps(result),
                        commit_id=result.get('properties', {}).get('commit', ""),
                        author_email=result.get('properties', {}).get('email', ""),
                        is_new=(old == 0)
                    )
                    vuln.save()
        scan.update_vulnerability_count()
    except json.decoder.JSONDecodeError:
        return JsonResponse({'message': "Unprocessable Entity"}, status=422)
    return {}
