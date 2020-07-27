import pkgutil
from importlib import import_module
import inspect
from types import ModuleType

import famapy.metamodels
from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.operations.AbstractOperation import Operation
from famapy.core.operations.Products import ProductsOperation
from famapy.core.operations.Valid import Valid
from famapy.core.transformations.TextToModel import TextToModel
from famapy.core.transformations.ModelToText import ModelToText
from famapy.core.transformations.ModelToModel import ModelToModel


class DiscoverMetamodels(object):
    def __init__(self):
        self.metamodels = self.discover()

    def iter_namespace(self, ns_pkg: ModuleType):
        prefix = ns_pkg.__name__ + "."
        return pkgutil.iter_modules(ns_pkg.__path__, prefix)

    def search_classes(self, submodule):
        classes = []
        for _, file_name, ispkg in self.iter_namespace(submodule):
            if ispkg:
                classes += self.search_classes(import_module(file_name))
            else:
                _file = import_module(file_name)
                classes += inspect.getmembers(_file, inspect.isclass)
        return classes

    def discover(self) -> dict:
        """ Generate a dictionaty with metamodels and its submodules. The
        submodules can be model, transformations and operations. Example:
        {
            'fm': {
                'module': module,
                'models': {'VariabilityModel': ['FeatureModel']},
                'transformations': {
                    'TextToModel': {'ext': 'XMLTransformation'},
                    'ModelToText': {'ext': 'XMLTransformation'},
                    'ModelToModel': {'ext ext': 'XMLTransformation'},
                },
                'operations': {'Valid': 'XMLTransformation'},
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

            # Search submodules: models, transformations y operations
            for _, submodule_name, ispkg in self.iter_namespace(module):
                if not ispkg:
                    continue
                submodule = import_module(submodule_name)
                submodule_name = submodule_name.split('.')[-1]
                if submodule_name == 'models':
                    metamodels[name][submodule_name] = {'VariabilityModel': []}
                elif submodule_name == 'operations':
                    metamodels[name][submodule_name] = {}
                elif submodule_name == 'transformations':
                    metamodels[name][submodule_name] = {'TextToModel': {}, 'ModelToText': {}, 'ModelToModel': {}}
                else:
                    continue

                classes = self.search_classes(submodule)
                for class_name, _class in classes:
                    if not _class.__module__.startswith(submodule.__package__):
                        continue  # Exclude modules not in current package
                    inherit = _class.mro()
                    if submodule_name == 'operations':
                        if ProductsOperation in inherit:
                            metamodels[name][submodule_name]['Products'] = _class
                        elif Valid in inherit:
                            metamodels[name][submodule_name]['Valid'] = _class
                        elif Operation in inherit:
                            metamodels[name][submodule_name][_class.__name__] = _class
                    elif submodule_name == 'transformations':
                        if TextToModel in inherit:
                            if not 'EXT_SRC' in dir(_class):
                                print(_class, " not contains EXT_SRC variable")
                                continue
                            ext = _class.EXT_SRC
                            metamodels[name][submodule_name]['TextToModel'][ext] = _class
                        elif ModelToText in inherit:
                            if not 'EXT_DST' in dir(_class):
                                print(_class, " not contains EXT_DST variable")
                                continue
                            ext = _class.EXT_DST
                            metamodels[name][submodule_name]['ModelToText'][ext] = _class
                        elif ModelToModel in inherit:
                            if not 'EXT_SRC' in dir(_class) or not 'EXT_DST' in dir(_class):
                                print(_class, " not contains EXT_SRC/EXT_DST variable")
                                continue
                            ext = "{} {}".format(_class.EXT_SRC, _class.EXT_DST)
                            metamodels[name][submodule_name]['ModelToModel'][ext] = _class
                    elif submodule_name == 'models':
                        if VariabilityModel in inherit:
                            metamodels[name][submodule_name]['VariabilityModel'].append(_class)
        return metamodels

    def reload(self):
        self.metamodels = self.discover()

    def __extract_metamodel_from_variability_model(self, vm: VariabilityModel):
        metamodel = None
        for key in self.metamodels.keys():
            if key in vm.__module__:
                metamodel = key
                break
        return metamodel

    def __extract_extension_from_filename(self, filename: str):
        return filename.split('.')[-1]

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

    def use_transformation_m2t(self, src: VariabilityModel, dst: str):
        mm = self.__extract_metamodel_from_variability_model(src)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        ext = self.__extract_extension_from_filename(dst)
        _class = self.metamodels[mm]['transformations']['ModelToText'][ext]
        transformation = _class(dst, src)
        transformation.transform()

    def use_transformation_t2m(self, src: str, dst: VariabilityModel) -> VariabilityModel:
        mm = self.__extract_metamodel_from_variability_model(dst)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        ext = self.__extract_extension_from_filename(src)
        _class = self.metamodels[mm]['transformations']['TextToModel'][ext]
        transformation = _class(src)
        return transformation.transform()

    def use_transformation_m2m(self, src: VariabilityModel, dst: str):
        mm = self.__extract_metamodel_from_variability_model(dst)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        src_ext = 'fm'  # TODO: extract extension of src metamodel
        ext = '{} {}'.format(src_ext, dst)
        _class = self.metamodels[mm]['transformations']['ModelToModel'][ext]
        transformation = _class(src)
        return transformation.transform()

    def use_operation(self, src: VariabilityModel, operation: Operation):
        mm = self.__extract_metamodel_from_variability_model(dst)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        _class = self.metamodels[mm]['operations'][operation.__name__]
        operation = _class()
        return operation.execute(src)

