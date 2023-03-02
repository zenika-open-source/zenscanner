from django.db import models
from uuid import uuid4
from core.models import User, Branch, Credential
from core.models.plugins.Formater import Formater


class Repository(models.Model):
    name = models.TextField()
    url = models.TextField()
    _credential = models.ForeignKey(Credential, on_delete=models.SET_DEFAULT, default=None, null=True, db_column='credential_id')
    uuid = models.UUIDField(default=uuid4)
    authkey = models.UUIDField(default=uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default="-1")
    scan_count = models.IntegerField(default=0)
    source_control = models.TextField(default="git")

    @property
    def branches(self):
        return [b.name for b in self.branch_set.all()]

    @property
    def credential(self):
        if self._credential:
            return self._credential
        else:
            if self.source_control == 'git':
                return Credential(type="PublicGit")
            elif self.source_control == 'svn':
                return Credential(type="PublicSvn")

    @credential.setter
    def credential(self, value):
        self._credential = value

    @property
    def formater(self):
        return Formater(repository=self).get_instance()

    def save(self, *args, **kwargs):
        if self.id:
            self.scan_count = self.scan_set.count()
        super(Repository, self).save(*args, **kwargs)

    def update_branches(self):
        branches = self.credential.get_instance().list_branches(self.url)
        available_branch = [b.name for b in self.branch_set.all()]
        for branch in branches:
            if branch not in available_branch:
                Branch.Branch(repository=self, name=branch).save()
