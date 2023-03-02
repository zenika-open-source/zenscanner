from core.utils.tasks import copy_to_volume, get_docker_client, volume_name
import requests
from django.conf import settings


class Uploaded:
    name = "Uploaded"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return self.kwargs.get('pull_url', None) is not None

    def run(self):
        client = get_docker_client()
        worker_token = self.kwargs.get('worker_token')
        v_name = volume_name(worker_token, 'HOME')
        client.volumes.create(v_name)
        try:
            if self.kwargs.get('pull_url').startswith("http"):
                response = requests.get(self.kwargs.get('pull_url'))
            else:
                response = requests.get(settings.API_URL + self.kwargs.get('pull_url'), headers={"Worker": worker_token})
        except Exception:
            raise Exception("Can't pull repository")

        copy_to_volume(volume_name(worker_token, 'HOME'), "src.tgz", response.content, None, "700")
        container = client.containers.run(
            'busybox',
            ['tar', '-xf', '/root/src.tgz', '-C', "/src"],
            volumes={
                worker_token: {'bind': '/src', 'mode': 'rw'},
                v_name: {'bind': '/root', 'mode': 'ro'},
            },
            auto_remove=True,
            detach=True
        )
        exit_code = container.wait(condition='removed')
        if exit_code['StatusCode'] == 1:
            raise Exception("Can't pull repository")
