from django.db import models
from core.models import Repository, ScanResult
from uuid import uuid4
import json
from celery.result import AsyncResult
from datetime import datetime
from django.utils.timezone import make_aware


class Scan(models.Model):
    created_at = models.DateTimeField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, default="-1")
    branch = models.TextField()
    uuid = models.UUIDField(default=uuid4)
    last_commit = models.TextField()
    warning_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    note_count = models.IntegerField(default=0)
    none_count = models.IntegerField(default=0)
    new_warning_count = models.IntegerField(default=0)
    new_error_count = models.IntegerField(default=0)
    new_note_count = models.IntegerField(default=0)
    new_none_count = models.IntegerField(default=0)
    _status = models.TextField(null=True, default='PENDING')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = make_aware(datetime.now())
        self.repository.save()
        super(Scan, self).save(*args, **kwargs)

    @property
    def branch_url(self):
        f = self.repository.formater
        if f:
            return f.fmt_base_branch_url(self)
        else:
            return ""

    @property
    def commit_url(self):
        f = self.repository.formater
        if f:
            return f.fmt_commit_url(self)
        else:
            return ""

    @property
    def scanners(self):
        try:
            sr = ScanResult.objects.get(task_id=self.uuid)
            sarif = json.loads(sr.sarif)
            scanners = set()
            for run in sarif.get('runs', {}):
                tool = run.get('tool', {}).get('driver', {}).get('name', None)
                if tool:
                    scanners.add(tool)
            return list(scanners)
        except Exception:
            return []

    @property
    def matched_scanners(self):
        scanners = {
            "new": set(),
            "old": set()
        }
        for vulneratility in self.vulnerability_set.only('tool'):
            if vulneratility.is_new:
                scanners['new'].add(vulneratility.tool)
            else:
                scanners['old'].add(vulneratility.tool)
        for key in scanners:
            scanners[key] = list(scanners[key])
        return scanners

    def update_vulnerability_count(self):
        warning_count = 0
        error_count = 0
        note_count = 0
        none_count = 0
        new_warning_count = 0
        new_error_count = 0
        new_note_count = 0
        new_none_count = 0
        for vulneratility in self.vulnerability_set.only('level'):
            level = vulneratility.level
            if level == 2:
                warning_count += 1
                if vulneratility.is_new:
                    new_warning_count += 1
            elif level == 3:
                error_count += 1
                if vulneratility.is_new:
                    new_error_count += 1
            elif level == 1:
                note_count += 1
                if vulneratility.is_new:
                    new_note_count += 1
            else:
                none_count += 1
                if vulneratility.is_new:
                    new_none_count += 1

        self.warning_count = warning_count
        self.error_count = error_count
        self.note_count = note_count
        self.none_count = none_count
        self.new_warning_count = new_warning_count
        self.new_error_count = new_error_count
        self.new_note_count = new_note_count
        self.new_none_count = new_none_count
        self.save()

    @property
    def status(self):
        if self._status not in ['SUCCESS', 'FAILURE', 'REVOKED']:
            task = AsyncResult(str(self.uuid))
            if task.status != self._status:
                self._status = task.status
                self.save()
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
