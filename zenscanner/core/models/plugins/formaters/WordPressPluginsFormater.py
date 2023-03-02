from urllib.parse import urlparse


class WordPressPluginsFormater(object):

    base_url = "https://plugins.svn.wordpress.org"
    domains = "plugins.svn.wordpress.org"

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        if kwargs.get("repository", None) is not None:
            self.repo_url = kwargs["repository"].url
            self.url_parts = urlparse(kwargs["repository"].url)

    def fmt_base_branch_url(self, scan):
        if scan.branch != "trunk":
            branch = "branches/" + scan.branch
        else:
            branch = "trunk"
        return "{}{}/{}/".format(self.base_url, self.url_parts.path, branch)

    def fmt_commit_url(self, scan):
        return self.fmt_base_branch_url(scan)

    def fmt_vulnerability_url(self, vulnerability):
        path = vulnerability.format_path()
        return "{}{}".format(
            self.fmt_base_branch_url(vulnerability.scan),
            path if not path.startswith('/') else path[1:]
        )
