import pkgutil
from importlib import import_module
from types import ModuleType

import famapy.metamodels


class DiscoverMetamodels(object):
    def __init__(self, prefix: str=''):
        self.prefix = prefix
        self.metamodels = self.discover()

    def iter_namespace(self, ns_pkg: ModuleType):
        if not self.prefix:
            self.prefix = ns_pkg.__name__ + "."
        return pkgutil.iter_modules(ns_pkg.__path__, self.prefix)

    def discover(self) -> list:
        metamodels = {}
        for finder, name, ispkg in self.iter_namespace(famapy.metamodels):
            metamodels[name] = import_module(name)
        return metamodels

    def reload(self):
        self.metamodels = self.discover()

    # TODO
    def get_valid_modules(self, extension):
        valids = []
        for name, model in self.discover().items():
            if model.test.check_extensions(extension):
                valids.append(model)
        return valids
