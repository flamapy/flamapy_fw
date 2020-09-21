import pkgutil
from importlib import import_module
import inspect
from types import ModuleType

import famapy.metamodels
from famapy.core.models import VariabilityModel
from famapy.core.operations import Operation, Products, Valid
from famapy.core.transformations import TextToModel, ModelToText, ModelToModel


class DiscoverMetamodels:
    def __init__(self):
        self.plugins = self.discover()

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
        """ Generate a dictionaty with plugins and its submodules. The
        submodules can be model, transformations and operations. Example:
        {
            'fm': {
                'module': module,
                'variability_model': 'FeatureModel',
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
        plugins = {}
        for _, name, ispkg in self.iter_namespace(famapy.metamodels):
            if not ispkg:
                continue
            module = import_module(name)
            plugins[name] = {}
            plugins[name]['module'] = module

            # Search submodules: models, transformations y operations
            for _, submodule_name, ispkg2 in self.iter_namespace(module):
                if not ispkg2:
                    continue
                submodule = import_module(submodule_name)
                submodule_name = submodule_name.split('.')[-1]
                if submodule_name == 'models':
                    plugins[name]['variability_model'] = None
                elif submodule_name == 'operations':
                    plugins[name][submodule_name] = {}
                elif submodule_name == 'transformations':
                    plugins[name][submodule_name] = {'TextToModel': {}, 'ModelToText': {}, 'ModelToModel': {}}
                else:
                    continue

                classes = self.search_classes(submodule)
                for _, _class in classes:
                    if not _class.__module__.startswith(submodule.__package__):
                        continue  # Exclude modules not in current package
                    inherit = _class.mro()
                    if submodule_name == 'operations':
                        if Products in inherit:
                            plugins[name][submodule_name]['Products'] = _class
                        elif Valid in inherit:
                            plugins[name][submodule_name]['Valid'] = _class
                        elif Operation in inherit:
                            plugins[name][submodule_name][_class.__name__] = _class
                    elif submodule_name == 'transformations':
                        if TextToModel in inherit:
                            ext = _class.get_source_extension()
                            plugins[name][submodule_name]['TextToModel'][ext] = _class
                        elif ModelToText in inherit:
                            ext = _class.get_destiny_extension()
                            plugins[name][submodule_name]['ModelToText'][ext] = _class
                        elif ModelToModel in inherit:
                            source_ext = _class.get_source_extension()
                            destiny_ext = _class.get_destiny_extension()
                            ext = "{} {}".format(source_ext, destiny_ext)
                            plugins[name][submodule_name]['ModelToModel'][ext] = _class
                    elif submodule_name == 'models':
                        if VariabilityModel in inherit:
                            plugins[name]['variability_model'] = _class
        return plugins

    def reload(self):
        self.plugins = self.discover()

    def __extract_plugin_from_variability_model(self, vm: VariabilityModel):
        plugin = None
        for key in self.plugins.keys():
            if key in vm.__module__:
                plugin = key
                break
        return plugin

    def __extract_plugin_from_extension(self, extension: str):
        plugin = None
        for key, values in self.plugins.items():
            vm = values.get('variability_model', None)
            if vm and vm.get_extension() == extension:
                plugin = key
                break
        return plugin

    def __extract_extension_from_filename(self, filename: str):
        return filename.split('.')[-1]

    def get_operations(self) -> list:
        """ Get the operations for all modules """
        operations = []
        for submodules in self.plugins.values():
            submodule_operation = submodules.get('operations', {})
            for submodule_name, submodule in submodule_operation.items():
                operations.append([submodule_name, submodule])
        return operations

    def get_transformations(self) -> list:
        """ Get the transformations for all modules """
        transformations = []
        for submodules in self.plugins.values():
            submodule_transformation = submodules.get('transformations', {})
            for submodule_name, submodule in submodule_transformation.items():
                transformations.append([submodule_name, submodule])
        return transformations

    def get_variability_models(self) -> list:
        return [sub.get('variability_model', None) for sub in self.plugins.values()]

    def get_plugin_by_name(self, plugin_name: str) -> str:
        plugins = list(filter(lambda k: k.find(plugin_name) >= 0, self.plugins.keys()))
        if len(plugins) < 1:
            print("plugin {} not found".format(plugin_name))
            return ''
        elif len(plugins) > 1:
            print("multiple plugin {} founds: {}. First selected".format(plugin_name, plugins))
            return plugins[0]
        else:
            return plugins[0]

    def use_transformation_m2t(self, src: VariabilityModel, dst: str):
        mm = self.__extract_plugin_from_variability_model(src)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        ext = self.__extract_extension_from_filename(dst)
        _class = self.plugins[mm]['transformations']['ModelToText'][ext]
        transformation = _class(dst, src)
        return transformation.transform()

    def use_transformation_t2m(self, src: str, dst: VariabilityModel) -> VariabilityModel:
        mm = self.__extract_plugin_from_extension(dst)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        ext = self.__extract_extension_from_filename(src)
        _class = self.plugins[mm]['transformations']['TextToModel'][ext]
        transformation = _class(src)
        return transformation.transform()

    def use_transformation_m2m(self, src: VariabilityModel, dst: str):
        mm = self.__extract_plugin_from_extension(dst)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        src_ext = src.get_extension()
        ext = '{} {}'.format(src_ext, dst)
        _class = self.plugins[mm]['transformations']['ModelToModel'][ext]
        transformation = _class(src)
        return transformation.transform()

    def use_operation(self, src: VariabilityModel, operation: str):
        mm = self.__extract_plugin_from_variability_model(src)
        if not mm:
            print("Metamodel not found from VariabilityModel")
        _class = self.plugins[mm]['operations'][operation]
        operation = _class()
        return operation.execute(src)
