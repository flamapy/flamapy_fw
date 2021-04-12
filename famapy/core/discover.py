import inspect
import logging
from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from typing import Any, Type

from famapy.core.config import PLUGIN_PATHS
from famapy.core.models import VariabilityModel
from famapy.core.operations import Operation
from famapy.core.plugins import (
    Operations,
    Plugin,
    Plugins
)
from famapy.core.transformations import Transformation


LOGGER = logging.getLogger('discover')


def filter_modules_from_plugin_paths() -> list[ModuleType]:
    results: list[ModuleType] = list()
    for path in PLUGIN_PATHS:
        try:
            module: ModuleType = import_module(path)
            results.append(module)
        except ModuleNotFoundError:
            LOGGER.exception('ModuleNotFoundError %s', path)
    return results


class DiscoverMetamodels:
    def __init__(self) -> None:
        self.module_paths = filter_modules_from_plugin_paths()
        self.plugins: Plugins = self.discover()

    def search_classes(self, module: ModuleType) -> list[Any]:
        classes = []
        for _, file_name, ispkg in iter_modules(
            module.__path__, module.__name__ + '.'  # type: ignore
        ):
            if ispkg:
                classes += self.search_classes(import_module(file_name))
            else:
                _file = import_module(file_name)
                classes += inspect.getmembers(_file, inspect.isclass)
        return classes

    def discover(self) -> Plugins:
        plugins = Plugins()
        for pkg in self.module_paths:
            for _, plugin_name, ispkg in iter_modules(
                pkg.__path__, pkg.__name__ + '.'  # type: ignore
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

    def reload(self) -> None:
        self.plugins = self.discover()

    def get_operations(self) -> list[Type[Operation]]:
        """ Get the operations for all modules """
        operations: list[Type[Operation]] = []
        for plugin in self.plugins:
            operations += plugin.operations
        return operations

    def get_transformations(self) -> list[Type[Transformation]]:
        """ Get the transformations for all modules """
        transformations: list[Type[Transformation]] = []
        for plugin in self.plugins:
            transformations += plugin.transformations
        return transformations

    def get_operations_by_plugin(self, plugin_name: str) -> Operations:
        return self.plugins.get_operations_by_plugin_name(plugin_name)

    def get_variability_models(self) -> list[VariabilityModel]:
        return self.plugins.get_variability_models()

    def get_plugins(self) -> list[str]:
        return self.plugins.get_plugin_names()

    def use_transformation_m2t(self, src: VariabilityModel, dst: str) -> str:
        plugin = self.plugins.get_plugin_by_variability_model(src)
        return plugin.use_transformation_m2t(src, dst)

    def use_transformation_t2m(self, src: str, dst: str) -> VariabilityModel:
        plugin = self.plugins.get_plugin_by_extension(dst)
        return plugin.use_transformation_t2m(src)

    def use_transformation_m2m(self, src: VariabilityModel, dst: str) -> VariabilityModel:
        plugin = self.plugins.get_plugin_by_extension(dst)
        return plugin.use_transformation_m2m(src, dst)

    def use_operation(self, src: VariabilityModel, operation: str) -> Operation:
        plugin = self.plugins.get_plugin_by_variability_model(src)
        return plugin.use_operation(operation, src)

    def use_operation_from_file(self, plugin_name: str, operation_name: str, file: str) -> Any:
        """
        Steps:
        * Search plugins by name
        * Search TextToModel transformation
        * Apply transformation
        * Apply operation
        """

        plugin: Plugin = self.plugins.get_plugin_by_name(plugin_name)
        variability_model = plugin.use_transformation_t2m(file)
        operation = plugin.use_operation(operation_name, variability_model)
        return operation.get_result()

    def use_operation_from_fm_file(
        self,
        plugin_name: str,
        operation_name: str,
        file: str
    ) -> Any:
        # TODO: change in a future for autodiscover transformation way
        fm_plugin: Plugin = self.plugins.get_plugin_by_name('fm_metamodel')
        vm_temp = fm_plugin.use_transformation_t2m(file)

        plugin: Plugin = self.plugins.get_plugin_by_name(plugin_name)
        variability_model = plugin.use_transformation_m2m(vm_temp, file)
        operation = plugin.use_operation(operation_name, variability_model)
        return operation.get_result()
