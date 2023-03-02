from core.utils.tasks import get_docker_client


class NoCreds:
    name = "NoCreds"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return self.kwargs.get('credential', None) is None and not self.kwargs.get('pull_url') and self.kwargs.get('repository')['source_control'] == "git"

    def run(self):
        repository = self.kwargs.get('repository')
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        branch = self.kwargs.get('branch', None)
        if branch:
            command = ['clone', repository['url'], "--branch", branch, "/src"]
        else:
            command = ['clone', repository['url'], "/src"]
        try:
            client.containers.run(
                'alpine/git',
                command,
                volumes={worker_token: {'bind': '/src', 'mode': 'rw'}},
                auto_remove=True
            )
        except Exception:
            raise Exception("Can't pull repository")
