

class GithubFormater(object):

    base_api_url = "https://api.github.com"
    base_url = "https://github.com"
    authorization_token = "Token {}"
    domains = "github.com"

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        if kwargs.get("repo_url", None) is not None:
            self.repo_url = kwargs["repo_url"]
            self.parse_repo_url()
        if kwargs.get("repository", None) is not None:
            self.repo_url = kwargs["repository"].url
            self.parse_repo_url()
        if kwargs.get("repo_name", None):
            self.repo_name = kwargs["repo_name"]
        if kwargs.get("repo_owner", None):
            self.repo_owner = kwargs["repo_owner"]

    def fmt_base_branch_url(self, scan):

        url = "{}/{}/{}/tree/{}".format(
            self.base_url,
            self.repo_owner,
            self.repo_name,
            scan.branch
        )

        return url

    def fmt_commit_url(self, scan):

        url = "{}/{}/{}/commit/{}".format(
            self.base_url,
            self.repo_owner,
            self.repo_name,
            scan.last_commit
        )

        return url

    def fmt_last_commit_url_for_all_branches(self):

        url = "{}/repos/{}/{}/branches".format(
            self.base_api_url,
            self.repo_owner,
            self.repo_name,
        )

        return url

    def fmt_last_commit_for_branch(self, branch):
        url = "{}/repos/{}/{}/branches/{}".format(
            self.base_api_url,
            self.repo_owner,
            self.repo_name,
            branch
        )

        return url

    def fmt_auth_header(self, token, headers={}):
        headers["Authorization"] = "token {}".format(token)
        return headers

    def parse_repo_url(self):
        self.repo_url.split(self.base_url)[1].split("/")
        repo_info = self.repo_url.split(self.base_url)[1].split("/")[1:3]

        self.repo_owner = repo_info[0]
        self.repo_name = repo_info[1]

        if self.repo_name[-4:] == ".git":
            self.repo_name = self.repo_name[:-4]

    def fmt_validate_url(self):
        return self.base_api_url + "/user"

    def fmt_repos_list(self, page=None):
        if not page:
            return self.base_api_url + "/user/repos"
        else:
            return self.base_api_url + "/user/repos?page={}".format(page)

    def fmt_vulnerability_url(self, vulnerability):
        path = vulnerability.format_path()
        branch = vulnerability.commit_id if vulnerability.commit_id else vulnerability.scan.branch
        return "{}/{}/{}/tree/{}{}".format(
            self.base_url,
            self.repo_owner,
            self.repo_name,
            branch,
            path if path.startswith('/') else "/" + path
        )
