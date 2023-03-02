import requests

raw_pack = """0014command=ls-refs
0014agent=git/2.38.10016object-format=sha100010009peel
001bref-prefix refs/heads/
0000"""


class PublicGit():
    name = "PublicGit"

    def __init__(self, credential):
        credential.uuid = None

    def validate(self):
        return False

    def list_branches(self, url):
        if not url.endswith(".git"):
            url += ".git"

        headers = {
            'git-protocol': 'version=2',
        }

        res = requests.post(url + '/git-upload-pack', headers=headers, data=raw_pack)

        return [b.split('refs/heads/')[1] for b in res.text.split('\n')[:-1]]

    def get_last_commit_for_branches(self, url):
        if not url.endswith(".git"):
            url += ".git"

        headers = {
            'git-protocol': 'version=2',
        }

        res = requests.post(url + '/git-upload-pack', headers=headers, data=raw_pack)

        return [{
            "name": b.split('refs/heads/')[1],
            "last_commit": b[4:44]
        } for b in res.text.split('\n')[:-1]]
