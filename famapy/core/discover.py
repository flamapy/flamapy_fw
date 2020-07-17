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

    def discover(self) -> list:
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

    def get_operations(self):
        """ Get the operations for all modules """
        operations = []
        for metamodel, submodules in self.metamodels.items():
            submodule_operation = submodules.get('operations', {})
            for submodule_name, submodule in submodule_operation.items():
                operations.append([submodule_name, submodule])
        return operations

    def get_transformations(self):
        """ Get the transformations for all modules """
        transformations = []
        for metamodel, submodules in self.metamodels.items():
            submodule_transformation = submodules.get('transformations', {})
            for submodule_name, submodule in submodule_transformation.items():
                transformations.append([submodule_name, submodule])
        return transformations

    def get_models(self):
        models = []
        for metamodel, submodules in self.metamodels.items():
            submodule_model = submodules.get('model', {})  # TODO: Change folder name
            for submodule_name, submodule in submodule_model.items():
                models.append([submodule_name, submodule])
        return models

    def use_transformation(self, src, dst, filename):
        # transformation puede ser:'load/save/transform' que es 'modelToText/textToModel/Transform'
        mm_src = self.metamodels.get(src)
        mm_dst = self.metamodels.get(dst)

        if mm_src and mm_dst:  # m2m
            vm = mm_dst.get('variability_model')
            res = mm_dst.transform(vm)
            print("Check si existe el modulo")
        elif mm_src and not mm_dst:  # t2m
            res = mm_src.transform(filename)
        elif not mm_src and mm_dst:  # m2t
            res = mm_dst.transform(filename)
        else:
            print("necesitamos src o/y dst")
        return res

    def use_operation(self, metamodel, operation):
        mm = self.metamodels.get(metamodel)
        # Check que existe mm
        trans = mm.get('operations').get(operation)
        # Check que existe trans
        return trans.execute()
