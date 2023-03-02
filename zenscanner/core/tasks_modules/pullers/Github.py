from core.utils.tasks import copy_to_volume, get_docker_client, volume_name


class Github:
    name = "Github"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        if self.kwargs.get('credential', None):
            return self.kwargs.get('credential').get('type', '') == 'Github' and not self.kwargs.get('pull_url')
        return False

    def inject_credentials(self):
        worker_token = self.kwargs.get('worker_token')
        credential = self.kwargs.get('credential')

        copy_to_volume(volume_name(worker_token, 'HOME'), "git-askpass-helper.sh", "#!/bin/sh\nexec echo \"{}\"".format(credential['value']), None, "700")

    def run(self):
        repository = self.kwargs.get('repository')
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        v_name = volume_name(worker_token, 'HOME')
        client.volumes.create(v_name)
        self.inject_credentials()
        branch = self.kwargs.get('branch', None)
        if branch:
            command = ['clone', repository['url'], "--branch", branch, "/src"]
        else:
            command = ['clone', repository['url'], "/src"]
        container = client.containers.run(
            'alpine/git',
            command,
            volumes={
                worker_token: {'bind': '/src', 'mode': 'rw'},
                v_name: {'bind': '/root', 'mode': 'ro'},
            },
            environment={"GIT_ASKPASS": "/root/git-askpass-helper.sh"},
            auto_remove=True,
            detach=True
        )
        exit_code = container.wait(condition='removed')
        client.volumes.get(v_name).remove()
        if exit_code['StatusCode'] == 128:
            raise Exception("Can't pull repository")
