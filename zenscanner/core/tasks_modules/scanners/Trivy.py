from core.utils.tasks import get_docker_client, get_volume_file_content, execute_command_in_volume
import time
import json
from docker.errors import NotFound


class Trivy:
    name = "Trivy"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        file_list = [
            "Gemfile.lock",
            "Pipfile.lock",
            "requirements.txt"
            "poetry.lock",
            "composer.lock",
            "package-lock.json",
            "yarn.lock",
            "packages.lock.json",
            "*.jar",
            "pom.xml"
            "*.war",
            "*.ear",
            "go.sum",
        ]

        args = ["-iname {}".format(i) for i in file_list]
        args = " -or ".join(args)
        args = "find " + args
        args = args.split(" ")

        return len(execute_command_in_volume(self.kwargs.get('worker_token'), args).output) > 0

    def run(self):
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        try:
            client.volumes.get('trivy-cache')
        except NotFound:
            client.volumes.create('trivy-cache')
        container = client.containers.run(
            'aquasec/trivy:0.29.2',
            'fs --format sarif -o /src/trivy.sarif /src',
            volumes={
                worker_token: {'bind': '/src', 'mode': 'rw'},
                'trivy-cache': {'bind': '/root/.cache/trivy/', 'mode': 'rw'}
            },
            auto_remove=True,
            detach=True
        )
        container.wait(condition="removed")
        time.sleep(0.5)
        content = json.loads(get_volume_file_content(worker_token, "trivy.sarif"))
        for run in content['runs']:
            for result in run['results']:
                full_value = result['message']['text'].split('\n')
                result['message']['text'] = "{} - {}".format(full_value[0].replace('Package: ', ''), full_value[1].replace('Installed Version: ', ''))
        return json.dumps(content).encode()
