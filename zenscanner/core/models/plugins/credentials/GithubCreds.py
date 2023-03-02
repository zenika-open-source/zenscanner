from requests import get
from core.models.plugins.formaters.GithubFormater import GithubFormater


class GithubCreds():
    name = "Github"

    can_sync = True
    can_list_branches = True

    def __init__(self, credential):
        self.token = credential.raw_value
        self.credential = credential

        self.can_sync = self.credential.allow_sync

    def validate(self):
        f = GithubFormater()
        if len(self.token) == 40:
            response = get(
                url=f.fmt_validate_url(),
                headers=f.fmt_auth_header(self.token)
            )
            if 'id' in response.json() and response.status_code == 200:
                return True
        return False

    def list(self, **kwargs):
        f = GithubFormater()
        page = kwargs.get("page", "1")
        response = get(
            url=f.fmt_repos_list(page),
            headers=f.fmt_auth_header(self.token)
        )
        return response.json()

    def list_branches(self, repo_url):
        f = GithubFormater(repo_url=repo_url)

        response = get(
            url=f.fmt_last_commit_url_for_all_branches(),
            headers=f.fmt_auth_header(self.token)
        )

        if response.status_code == 200:
            return [b['name'] for b in response.json()]
        return []

    def get_last_commit_for_branches(self, repo_url):
        f = GithubFormater(repo_url=repo_url)

        response = get(
            url=f.fmt_last_commit_url_for_all_branches(),
            headers=f.fmt_auth_header(self.token)
        )

        if response.status_code == 200:
            return [{"name": b['name'], "last_commit": b['commit']['sha']} for b in response.json()]
        return []

    def sync(self):
        from core.models import Repository, Branch
        from django.core.exceptions import ObjectDoesNotExist
        page = 0
        repositories = [1]
        while len(repositories) > 0:
            page += 1
            repositories = self.list(page=page)
            for repository in repositories:
                if Repository.objects.filter(owner=self.credential.owner, url=repository['html_url']).count() == 0:
                    Repository(url=repository['html_url'], name=repository['name'], owner=self.credential.owner, credential=self.credential).save()
                repo = Repository.objects.get(owner=self.credential.owner, url=repository['html_url'])
                for branch in self.list_branches(repo.url):
                    try:
                        Branch.objects.get(repository=repo, name=branch)
                    except ObjectDoesNotExist:
                        Branch(repository=repo, name=branch).save()
