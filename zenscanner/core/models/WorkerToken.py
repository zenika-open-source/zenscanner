from django.db import models
from uuid import uuid4
from core.models.Scan import Scan
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware


class WorkerToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, default="-1")
    deleted_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.deleted_at is None:
            self.deleted_at = make_aware(datetime.now() + timedelta(days=7))
            super(WorkerToken, self).save(*args, **kwargs)

    def is_valid(self):
        return self.deleted_at > timezone.now()
