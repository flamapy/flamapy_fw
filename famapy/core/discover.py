import logging
from pkgutil import iter_modules
from importlib import import_module
import inspect
from types import ModuleType
from typing import List

from famapy.core.config import PLUGIN_PATHS

from famapy.core.models import VariabilityModel
from famapy.core.operations import Operation
from famapy.core.transformations import Transformation
from famapy.core.plugins import (
    Plugin,
    Plugins
)


LOGGER = logging.getLogger('discover')


def filter_modules_from_plugin_paths() -> List[ModuleType]:
    results: List[ModuleType] = list()
    for path in PLUGIN_PATHS:
        try:
            module: ModuleType = import_module(path)
            results.append(module)
        except ModuleNotFoundError:
            LOGGER.exception('ModuleNotFoundError %s', path)
    return results


class DiscoverMetamodels:
    def __init__(self):
        self.module_paths = filter_modules_from_plugin_paths()
        self.plugins: Plugins = self.discover()

    def search_classes(self, module):
        classes = []
        for _, file_name, ispkg in iter_modules(
            module.__path__, module.__name__ + '.'
        ):
            if ispkg:
                classes += self.search_classes(import_module(file_name))
            else:
                _file = import_module(file_name)
                classes += inspect.getmembers(_file, inspect.isclass)
        return classes

    def discover(self) -> dict:
        plugins = Plugins()
        for pkg in self.module_paths:
            for _, plugin_name, ispkg in iter_modules(
                pkg.__path__, pkg.__name__ + '.'
            ):
                if not ispkg:
                    continue
                module = import_module(plugin_name)
                plugin = Plugin(module=module)

                classes = self.search_classes(module)

                for _, _class in classes:
                    if not _class.__module__.startswith(module.__package__):
                        continue  # Exclude modules not in current package
                    inherit = _class.mro()

                    if Operation in inherit:
                        plugin.append_operation(_class)
                    elif Transformation in inherit:
                        plugin.append_transformations(_class)
                    elif VariabilityModel in inherit:
                        plugin.variability_model = _class
                plugins.append(plugin)
        return plugins

    def reload(self):
        self.plugins = self.discover()

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

    def get_operations_by_plugin(self, plugin_name: str) -> List[str]:
        return self.plugins.get_operations_by_plugin_name(plugin_name)

    def get_variability_models(self) -> List[VariabilityModel]:
        return self.plugins.get_variability_models()

    def get_plugins(self) -> List[str]:
        return self.plugins.get_plugin_names()

    def use_transformation_m2t(self, src: VariabilityModel, dst: str):
        plugin = self.plugins.get_plugin_by_variability_model(src)
        return plugin.use_transformation_m2t(src, dst)

    def use_transformation_t2m(self, src: str, dst: str) -> VariabilityModel:
        plugin = self.plugins.get_plugin_by_extension(dst)
        return plugin.use_transformation_t2m(src)

    def use_transformation_m2m(self, src: VariabilityModel, dst: str):
        plugin = self.plugins.get_plugin_by_extension(dst)
        return plugin.use_transformation_m2m(src, dst)

    def use_operation(self, src: VariabilityModel, operation: str):
        plugin = self.plugins.get_plugin_by_variability_model(src)
        return plugin.use_operation(operation, src)

    def use_operation_from_file(self, plugin: str, operation: str, file: str):
        """
        Steps:
        * Search plugins by name
        * Search TextToModel transformation
        * Apply transformation
        * Apply operation
        """

        plugin: Plugin = self.plugins.get_plugin_by_name(plugin)
        variability_model = plugin.use_transformation_t2m(file)
        operation = plugin.use_operation(operation, variability_model)
        return operation.get_result()

''' This is to be defined
    def use_operation_from_fm_file(
        self,
        plugin: str,
        operation: str,
        file: str
    ):
        # TODO: change in a future for autodiscover transformation way
        fm_plugin: Plugin = self.plugins.get_plugin_by_name('fm_metamodel')
        vm_temp = fm_plugin.use_transformation_t2m(file)

        plugin: Plugin = self.plugins.get_plugin_by_name(plugin)
        variability_model = plugin.use_transformation_m2m(vm_temp, file)
        operation = plugin.use_operation(operation, variability_model)
        return operation.get_result()
'''