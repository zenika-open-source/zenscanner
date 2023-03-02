import glob
import importlib
import json
import os
import tarfile
import tempfile
import re

import core.tasks_modules
import docker
import requests
from django.conf import settings

EMPTY_SARIF = {
    "version": "2.1.0",
    "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": ""
                }
            },
            "results": []
        }
    ]
}


def get_docker_client():
    return docker.from_env()


def volume_name(worker_token, t):
    type = {
        'SRC': '',
        'HOME': '-home',
    }
    return worker_token + type.get(t, "")


def copy_to_volume(volume_name, filename, content, owner=None, mode=None):
    client = get_docker_client()
    directory = os.path.dirname(filename)
    full_directory = os.path.join('/volume', directory)
    short_filename = os.path.basename(filename)
    full_filename = os.path.join(full_directory, short_filename)
    container = client.containers.run('busybox', ['tail', '-f', '/dev/null'],
                                      volumes={volume_name: {'bind': '/volume', 'mode': 'rw'}},
                                      auto_remove=True,
                                      detach=True
                                      )
    if directory:
        container.exec_run(['mkdir', '-p', full_directory])
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        if type(content) == bytes:
            with open(short_filename, "wb") as f:
                f.write(content)
        else:
            with open(short_filename, "w") as f:
                f.write(content)
        tar = tarfile.open('copy_to_volume.tar', mode='w')
        try:
            tar.add(short_filename)
        finally:
            tar.close()
        container.put_archive(full_directory, open('copy_to_volume.tar', 'rb').read())
    if owner:
        container.exec_run(['sh', '-c', 'chown {} {}'.format(owner, full_filename)])
    else:
        container.exec_run(['sh', '-c', 'chown $(id -u):$(id -g) ' + full_filename])
    if mode:
        container.exec_run(['sh', '-c', 'chmod {} {}'.format(mode, full_filename)])

    container.remove(force=True)


def execute_command_in_volume(volume_name, command):
    client = get_docker_client()
    container = client.containers.run('busybox', ['tail', '-f', '/dev/null'],
                                      volumes={volume_name: {'bind': '/volume', 'mode': 'rw'}},
                                      auto_remove=True,
                                      detach=True,
                                      working_dir="/volume",
                                      )
    logs = container.exec_run(command)
    container.remove(force=True)
    return logs


def get_volume_file_content(volume_name, filename):
    client = get_docker_client()
    directory = os.path.dirname(filename)
    full_directory = os.path.join('/volume', directory)
    short_filename = os.path.basename(filename)
    full_filename = os.path.join(full_directory, short_filename)
    container = client.containers.run('busybox', ['tail', '-f', '/dev/null'],
                                      volumes={volume_name: {'bind': '/volume', 'mode': 'rw'}},
                                      auto_remove=True,
                                      detach=True
                                      )
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.chdir(tmpdirname)
            bits, stat = container.get_archive(full_filename)
            with open('archive.tar', 'wb') as archive:
                for chunk in bits:
                    archive.write(chunk)
            try:
                tar = tarfile.open("archive.tar")
                content = tar.extractfile(short_filename).read()
            finally:
                tar.close()
    except Exception:
        content = "".encode()
    finally:
        container.remove(force=True)
    return content


def load_plugins(plugin_type, **kwargs):
    plugins = {}
    modules_location = os.path.dirname(os.path.abspath(core.tasks_modules.__file__))
    for file in glob.glob('{}/{}/*.py'.format(modules_location, plugin_type)):
        name = os.path.basename(file)[:-3]
        if name != "__init__":
            module = importlib.import_module("core.tasks_modules.{}.{}".format(plugin_type, name))
            module_class = getattr(module, name)
            plugins[name] = module_class(**kwargs)
    return plugins


def get_empty_sarif(tool_name):
    sarif = EMPTY_SARIF
    sarif['runs'][0]["tool"]["driver"]["name"] = tool_name
    return json.dumps(sarif)


class Scanner():

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for required in ['worker_token', 'task_id']:
            if required not in self.kwargs:
                raise BaseException(required + ' is required')
        self.headers = {
            "Worker": self.kwargs.get('worker_token')
        }
        self.client = get_docker_client()
        self.fetch_repository()
        self.fetch_credential()
        self.client.volumes.create(self.kwargs.get('worker_token'))

    def fetch_repository(self):
        self.kwargs['repository'] = requests.get(
            settings.API_URL + "/api/workers/repository",
            headers=self.headers
        ).json()

    def fetch_credential(self):
        if self.kwargs['repository'].get('credential', None):
            self.kwargs['credential'] = requests.get(
                settings.API_URL + "/api/workers/repository/credential",
                headers=self.headers
            ).json()

    def lookup_repo_info(self):
        client = get_docker_client()
        if self.kwargs['repository']['source_control'] == 'git':
            container = client.containers.run(
                'alpine/git',
                ['-f', '/dev/null'],
                detach=True,
                entrypoint="tail",
                working_dir="/src",
                volumes={self.kwargs.get('worker_token'): {'bind': '/src', 'mode': 'rw'}}
            )
            try:
                branch = container.exec_run("git branch --show-current")
                if branch.exit_code == 0:
                    self.kwargs['branch'] = branch.output.strip().decode()
                last_commit = container.exec_run("git --no-pager log --format='%H' -n 1")
                if last_commit.exit_code == 0:
                    self.kwargs['last_commit'] = last_commit.output.strip().decode()
            except Exception:
                pass
            finally:
                container.remove(force=True)
        elif self.kwargs['repository']['source_control'] == 'svn':
            container = client.containers.run(
                'jgsqware/svn-client',
                ['-f', '/dev/null'],
                detach=True,
                entrypoint="tail",
                working_dir="/src",
                volumes={self.kwargs.get('worker_token'): {'bind': '/src', 'mode': 'rw'}}
            )
            try:
                infos = container.exec_run("svn info /src")
                if infos.exit_code == 0:
                    for line in infos.output.decode().split("\n"):
                        i = line.split(':', maxsplit=1)
                        if i[0] == 'URL':
                            self.kwargs['branch'] = i[1].split('/')[-1]
                        elif i[0] == 'Last Changed Rev':
                            self.kwargs['last_commit'] = i[1].strip()
            except Exception:
                pass
            finally:
                container.remove(force=True)

    def cleanup(self):
        volumes = self.client.volumes.list()
        for v in volumes:
            if re.compile("^[0-9a-f]{64}$").match(v.id) or re.compile(self.kwargs.get('worker_token')).match(v.id):
                try:
                    v.remove()
                except Exception:
                    pass
        requests.delete(settings.API_URL + "/api/workers", headers=self.headers)

    def run_pullers(self):
        pullers = load_plugins("pullers", **self.kwargs)
        for puller in pullers.values():
            if puller.is_runnable():
                puller.run()
        self.lookup_repo_info()
        self.put_infos()

    def run_scanners(self):
        scanners = load_plugins("scanners", **self.kwargs)
        for s in scanners.values():
            if s.is_runnable():
                self.put_result(s.name, s.run())

    def put_result(self, plugin_name, result):
        if len(result) == 0:
            result = get_empty_sarif(plugin_name)

        requests.put(
            settings.API_URL + "/api/workers/result",
            data=result,
            headers=self.headers
        )

    def put_infos(self):
        data = {}
        if self.kwargs.get('branch', None):
            data["branch"] = self.kwargs['branch']
        if self.kwargs.get('last_commit', None):
            data["last_commit"] = self.kwargs['last_commit']
        requests.put(
            settings.API_URL + "/api/workers/information",
            json=data,
            headers=self.headers
        )
