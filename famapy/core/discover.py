import pkgutil
from importlib import import_module
import inspect
from types import ModuleType

import famapy.metamodels


class DiscoverMetamodels(object):
    def __init__(self):
        self.metamodels = self.discover()

    def iter_namespace(self, ns_pkg: ModuleType):
        prefix = ns_pkg.__name__ + "."
        return pkgutil.iter_modules(ns_pkg.__path__, prefix)

    def discover(self) -> dict:
        """ Generate a dictionaty with metamodels and its submodules. The
        submodules can be model, transformations and operations. Example:
        {
            'fm': {
                'module': module,
                'model': {'VariabilityModel': 'FeatureModel'},
                'transformation': {'TextToModel': 'XMLTransformation'},
                ...
            },
        }
        """
        metamodels = {}
        for _, name, ispkg in self.iter_namespace(famapy.metamodels):
            if not ispkg:
                continue
            module = import_module(name)
            metamodels[name] = {}
            metamodels[name]['module'] = module

            # Search submodules: model, transformations y operations
            for _, submodule_name, ispkg in self.iter_namespace(module):
                if not ispkg:
                    continue
                submodule = import_module(submodule_name)
                submodule_name = submodule_name.split('.')[-1]
                metamodels[name][submodule_name] = {}
                for _, file_name, ispkg in self.iter_namespace(submodule):
                    if ispkg:
                        # TODO: recursive iter for found modules in subfolder
                        pass
                    # TODO: Check file_name is a valid file
                    try:
                        _file = import_module(file_name)
                    except:
                        continue
                    classes = inspect.getmembers(_file, inspect.isclass)
                    for class_name, _class in classes:
                        # TODO: filter by name, inherit and module?
                        #print("Herencia", _class.mro())
                        metamodels[name][submodule_name][class_name] = _class
        return metamodels

    def reload(self):
        self.metamodels = self.discover()

    def get_operations(self) -> list:
        """ Get the operations for all modules """
        operations = []
        for metamodel, submodules in self.metamodels.items():
            submodule_operation = submodules.get('operations', {})
            for submodule_name, submodule in submodule_operation.items():
                operations.append([submodule_name, submodule])
        return operations

    def get_transformations(self) -> list:
        """ Get the transformations for all modules """
        transformations = []
        for metamodel, submodules in self.metamodels.items():
            submodule_transformation = submodules.get('transformations', {})
            for submodule_name, submodule in submodule_transformation.items():
                transformations.append([submodule_name, submodule])
        return transformations

    def get_models(self) -> list:
        models = []
        for metamodel, submodules in self.metamodels.items():
            submodule_model = submodules.get('model', {})  # TODO: Change folder name
            for submodule_name, submodule in submodule_model.items():
                models.append([submodule_name, submodule])
        return models

    def get_metamodel_by_name(self, metamodel_name: str) -> str:
        metamodels = list(filter(lambda k: k.find(metamodel_name) >= 0, self.metamodels.keys()))
        if len(metamodels) < 1:
            print("metamodel {} not found".format(metamodel_name))
            return ''
        elif len(metamodels) > 1:
            print("multiple metamodel {} founds: {}. First selected".format(metamodel_name, metamodels))
            return metamodels[0]
        else:
            return metamodels[0]

    def use_transformation(self, src: str, dst: str, filename: str):
        if src and dst:  # m2m
            mm_src = self.get_metamodel_by_name(src)
            mm_dst = self.get_metamodel_by_name(dst)
            if not mm_src or not mm_dst:
                res = ''
            else:
                mm_src = self.get_metamodel_by_name(src)
                mm_dst = self.get_metamodel_by_name(dst)
                __vm = self.metamodels[mm_src].get('model', {}).get('VariabilityModel')
                __class = self.metamodels[mm_dst].get('transformations', {}).get('ModelToModel')
                instance = __class(__vm)
                res = instance.transform(filename)
        elif src and not dst:  # t2m
            mm_src = self.get_metamodel_by_name(src)
            __class = self.metamodels[mm_src].get('transformations', {}).get('TextToModel')
            instance = __class()
            res = instance.transform(filename)
        elif not src and dst:  # m2t
            mm_dst = self.get_metamodel_by_name(dst)
            __class = self.metamodels[mm_dst].get('transformations', {}).get('ModelToText')
            instance = __class()
            res = instance.transform(filename)
        else:
            print("necesitamos src o/y dst")
        return res

    def use_operation(self, src: str, operation: str):
        mm = self.get_metamodel_by_name(src)
        operations = self.metamodels[mm].get('operations', {})
        __class = operations.get(operation)
        if not __class:
            print("operation {} not found. Availables operations are: {}".format(operation, operations.keys()))
            res = ''
        else:
            instance = __class()
            res = instance.execute()
        return res

