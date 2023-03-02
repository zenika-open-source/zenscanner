import uuid

from core.models import User
from django.db import models
from django.utils import timezone


class AccessToken(models.Model):
    label = models.TextField()
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default="-1")
    deleted_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.deleted_at > timezone.now() if self.deleted_at else True
