
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import check_password
from uuid import uuid4
from django.db import models


class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        db_table = 'users'

    def is_good_password(self, password):
        return check_password(password, self.password)
