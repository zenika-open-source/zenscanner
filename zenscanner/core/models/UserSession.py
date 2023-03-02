from django.db import models
from uuid import uuid4
from core.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from django.conf import settings


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="-1")
    deleted_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.deleted_at is None:
            self.deleted_at = make_aware(datetime.now() + timedelta(seconds=settings.SESSION_DURATION))
            super(UserSession, self).save(*args, **kwargs)

    def is_valid(self):
        return self.deleted_at > timezone.now()
