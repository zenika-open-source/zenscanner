from django.db import models
from uuid import uuid4
from core.models import Repository


class ScanResult(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, default="-1")
    task_id = models.UUIDField(default=uuid4)
    branch = models.TextField()
    sarif = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_commit = models.TextField()
