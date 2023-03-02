import glob
import os
import importlib
import core.tasks_modules


def load_plugins(plugin_type):
    plugins = {}
    modules_location = os.path.dirname(os.path.abspath(core.tasks_modules.__file__))
    for file in glob.glob('{}/{}/*.py'.format(modules_location, plugin_type)):
        name = os.path.basename(file)[:-3]
        if name != "__init__":
            module = importlib.import_module("core.tasks_modules.{}.{}".format(plugin_type, name))
            module_class = getattr(module, name)
            plugins[name] = module_class
    return plugins


EXPORTERS = load_plugins("exporters")


class Exporter():

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if "worker_token" in self.kwargs:
            self.kwargs['scan'] = self.kwargs['worker_token'].scan
            self.kwargs['repository'] = self.kwargs['worker_token'].scan.repository

    def execute(self):
        for e in EXPORTERS:
            e = EXPORTERS[e](**self.kwargs)
            if e.is_runnable():
                e.run()
