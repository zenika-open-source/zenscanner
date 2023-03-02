from core.utils.tasks import get_docker_client


class NoCredsSvn:
    name = "NoCredsSvn"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return self.kwargs.get('credential', None) is None and not self.kwargs.get('pull_url') and self.kwargs.get('repository')['source_control'] == "svn"

    def run(self):
        repository = self.kwargs.get('repository')
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        branch = self.kwargs.get('branch', None)
        command = ['co', repository['url'] + "/trunk", "/src"]
        if branch:
            if branch != "trunk":
                command = ['co', repository['url'] + "/" + branch, "/src"]
        try:
            client.containers.run(
                'jgsqware/svn-client',
                command,
                volumes={worker_token: {'bind': '/src', 'mode': 'rw'}},
                auto_remove=True
            )
        except Exception:
            raise Exception("Can't pull repository")
