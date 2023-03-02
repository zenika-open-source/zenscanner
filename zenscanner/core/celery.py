import os

from celery import Celery
from celery.schedules import crontab
from core.utils.tasks import Scanner

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zenscanner.settings')

app = Celery('zenscanner')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_routes = {
    'core.celery.sync_repositories': {'queue': 'api'},
    'core.celery.autoscan': {'queue': 'api'},
    'core.celery.debug_task': {'queue': 'api'},
    'core.celery.run_scan': {'queue': 'scanner'},
    'core.celery.run_uploaded_scan': {'queue': 'scanner'}
}


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=0, hour=0), sync_repositories.s())
    sender.add_periodic_task(crontab(minute=0, hour=1), autoscan.s())


@app.task(bind=True)
def debug_task(self):
    self.update_state(state='RUNNING')
    self.update_state(state='SUCCESS')
    return "OK"


@app.task(bind=True)
def run_scan(self, worker_token, **kwargs):
    self.update_state(state='RUNNING')
    scanner = Scanner(worker_token=worker_token, task_id=self.request.id, **kwargs)
    scanner.run_pullers()
    scanner.run_scanners()
    scanner.cleanup()
    self.update_state(state='SUCCESS')
    return


@app.task(bind=True)
def run_uploaded_scan(self, worker_token, pull_url):
    self.update_state(state='RUNNING')
    scanner = Scanner(worker_token=worker_token, task_id=self.request.id, pull_url=pull_url)
    scanner.run_pullers()
    scanner.run_scanners()
    scanner.cleanup()
    self.update_state(state='SUCCESS')


@app.task(bind=True)
def sync_repositories(self):
    from core.models import Credential
    self.update_state(state='RUNNING')
    creds = Credential.objects.all()
    for cred in creds:
        instance = cred.get_instance()
        if hasattr(instance, "can_sync") and instance.can_sync:
            instance.sync()
    self.update_state(state='SUCCESS')
    return


@app.task(bind=True)
def autoscan(self):
    from core.models import Repository, Scan, WorkerToken, Branch
    from django.core.exceptions import ObjectDoesNotExist

    self.update_state(state='RUNNING')
    repos = Repository.objects.all()
    for repo in repos:
        scans = Scan.objects.filter(repository=repo)
        branches = None
        if repo.credential:
            cred = repo.credential.get_instance()
            branches = cred.get_last_commit_for_branches(repo.url)

        if branches:
            for branch in branches:
                try:
                    Branch.objects.get(repository=repo, name=branch['name'])
                except ObjectDoesNotExist:
                    Branch(repository=repo, name=branch['name']).save()

                def lookup_scans():
                    for scan in scans:
                        if scan.branch == branch['name'] and scan.last_commit == branch['last_commit']:
                            return
                    scan = Scan(repository=repo)
                    scan.save()
                    worker_token = WorkerToken(scan=scan)
                    worker_token.save()
                    run_scan.delay(worker_token.token, branch=branch['name'])
                lookup_scans()
    self.update_state(state='SUCCESS')
    return
