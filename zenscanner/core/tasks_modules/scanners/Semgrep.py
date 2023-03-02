from core.utils.tasks import get_docker_client, get_volume_file_content
from core.utils.sarif import Sarif, Result
import json
import time


class Semgrep:
    name = "Semgrep"
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return True

    def run(self):
        worker_token = self.kwargs.get('worker_token')
        client = get_docker_client()
        container = client.containers.run(
            'returntocorp/semgrep',
            '--config auto --config p/security-audit --json -o /src/semgrep.json /src',
            volumes={worker_token: {'bind': '/src', 'mode': 'rw'}},
            auto_remove=True,
            detach=True,
            user=0,  # Allow to export sarif in the src folder
        )

        container.wait(condition="removed")
        time.sleep(0.5)
        content = json.loads(get_volume_file_content(worker_token, "semgrep.json"))
        s = Sarif(name="Semgrep")
        for result in content['results']:
            r = Result(
                message=result['extra']['message'],
                level=result['extra']['severity'],
                rule=result['check_id'],
                filename=result['path'][4:],
                match=result['extra']['lines'],
                match_start=result['start']['line'],
                match_end=result['end']['line'],
            )

            s.add_result(r)
            s.add_rule(result['check_id'], result['check_id'], result['extra']['metadata'].get('source', ''))
        return json.dumps(s.to_json()).encode()
