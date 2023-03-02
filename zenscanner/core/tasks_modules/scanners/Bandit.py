from core.utils.tasks import get_docker_client, get_volume_file_content, execute_command_in_volume
import json
import time


class Bandit:
    name = "Bandit"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return len(execute_command_in_volume(self.kwargs.get('worker_token'), ["find", "-name", "*.py"]).output) > 0

    def run(self):
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        container = client.containers.run(
            'thomasfady/bandit-sarif',
            '-f sarif -r /src -o /src/bandit.sarif',
            volumes={worker_token: {'bind': '/src', 'mode': 'rw'}},
            auto_remove=True,
            detach=True
        )
        container.wait(condition="removed")
        time.sleep(0.5)
        content = json.loads(get_volume_file_content(worker_token, "bandit.sarif"))
        for run in content['runs']:
            del run['invocations']
            del run['properties']
            for result in run['results']:
                result['level'] = result['properties']['issue_severity']
        return json.dumps(content).encode()
