import glob
import os
import importlib
from urllib.parse import urlparse

MODULES_LOCATIONS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "formaters")


def load_formaters_domains():
    domains = {}
    for file in glob.glob('{}/*.py'.format(MODULES_LOCATIONS)):
        name = os.path.basename(file)[:-3]
        if name != "__init__":
            module = importlib.import_module("core.models.plugins.formaters.{}".format(name))
            module_class = getattr(module, name)
            if getattr(module_class, 'domains', None):
                if type(module_class.domains) is str:
                    domains[module_class.domains] = module_class
                else:
                    for domain in module_class.domains:
                        domains[domain] = module_class
    return domains


FORMATERS_DOMAINS = load_formaters_domains()


class Formater():

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def get_instance(self):
        if self.kwargs.get("repo_url", None):
            formater = FORMATERS_DOMAINS.get(urlparse(self.kwargs.get("repo_url")).netloc, None)
        if self.kwargs.get("repository", None):
            formater = FORMATERS_DOMAINS.get(urlparse(self.kwargs.get("repository").url).netloc, None)

        return formater(**self.kwargs) if formater else None
