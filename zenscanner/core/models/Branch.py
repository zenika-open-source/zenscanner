from django.db import models
from core.models.Repository import Repository


class Branch(models.Model):

    name = models.TextField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, default="-1")
