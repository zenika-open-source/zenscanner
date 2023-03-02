from core.utils.tasks import get_docker_client, get_volume_file_content
import time
import json


class Gitleaks:
    name = "Gitleaks"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return True

    def run(self):
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        args = 'detect -s /src -r /src/gitleaks.sarif -f sarif --no-git --exit-code=0'
        container = client.containers.run(
            'zricethezav/gitleaks:v8.15.1',
            args,
            user="root",
            volumes={worker_token: {'bind': '/src', 'mode': 'rw'}},
            auto_remove=True,
            detach=True,
        )
        container.wait(condition="removed")
        time.sleep(0.5)
        content = json.loads(get_volume_file_content(worker_token, "gitleaks.sarif"))
        content['runs'][0]['tool']['driver']['name'] = "Gitleaks"
        return json.dumps(content).encode()
