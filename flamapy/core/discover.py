import inspect
import logging
from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from typing import Any, Optional, Protocol, Type, runtime_checkable

from flamapy.core.config import PLUGIN_PATHS
from flamapy.core.exceptions import OperationNotFound
from flamapy.core.exceptions import TransformationNotFound
from flamapy.core.exceptions import ConfigurationNotFound
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.plugins import (
    Operations,
    Plugin,
    Plugins
)
from flamapy.core.transformations import Transformation
from flamapy.core.transformations.text_to_model import TextToModel
from flamapy.core.transformations.model_to_model import ModelToModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


LOGGER = logging.getLogger('discover')


@runtime_checkable
class OperationWithConfiguration(Protocol):
    def set_configuration(self, configuration: Configuration) -> None:
        pass


def filter_modules_from_plugin_paths() -> list[ModuleType]:
    results: list[ModuleType] = []
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
            module.__path__, module.__name__ + '.'
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

    def reload(self) -> None:
        self.plugins = self.discover()

    def get_operations(self) -> list[Type[Operation]]:
        """ Get the operations for all modules """
        operations: list[Type[Operation]] = []
        for plugin in self.plugins:
            operations += plugin.operations
        return operations

    def get_name_operations(self) -> list[str]:
        operations = []
        for operation in self.get_operations():
            operations.append(operation.__name__)
            base = operation.__base__.__name__
            if base != 'ABC':
                operations.append(base)

        return operations

    def get_transformations(self) -> list[Type[Transformation]]:
        """ Get transformations for all modules """
        transformations: list[Type[Transformation]] = []
        for plugin in self.plugins:
            transformations += plugin.transformations
        return transformations

    def get_transformations_t2m(self) -> list[Type[TextToModel]]:
        """ Get t2m transformations for all modules """

        transformations: list[Type[TextToModel]] = []
        for plugin in self.plugins:
            transformations += [
                t for t in plugin.transformations if issubclass(t, TextToModel)
            ]
        return transformations

    def get_transformations_m2m(self) -> list[Type[ModelToModel]]:
        """ Get m2m transformations for all modules """

        transformations: list[Type[ModelToModel]] = []
        for plugin in self.plugins:
            transformations += [
                t for t in plugin.transformations if issubclass(t, ModelToModel)
            ]
        return transformations

    def get_operations_by_plugin(self, plugin_name: str) -> Operations:
        return self.plugins.get_operations_by_plugin_name(plugin_name)

    def get_plugins_with_operation(self, operation_name: str) -> list[Plugin]:
        return [
            plugin for plugin in self.plugins
            if operation_name in self.get_name_operations_by_plugin(plugin.name)
        ]

    def get_name_operations_by_plugin(self, plugin_name: str) -> list[str]:
        operations = []
        for operation in self.get_operations_by_plugin(plugin_name):
            operations.append(operation.__name__)
            base = operation.__base__.__name__
            if base != 'ABC':
                operations.append(base)

        return operations

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

    def use_operation(self, src: VariabilityModel, operation_name: str) -> Operation:
        plugin = self.plugins.get_plugin_by_variability_model(src)
        operation = plugin.get_operation(operation_name)
        return plugin.use_operation(operation, src)

    def use_operation_from_file(
        self,
        operation_name: str,
        file: str,
        plugin_name: Optional[str] = None,
        configuration_file: Optional[str] = None
    ) -> Any:

        if operation_name not in self.get_name_operations():
            raise OperationNotFound()

        if plugin_name is not None:
            plugin = self.plugins.get_plugin_by_name(plugin_name)
            vm_temp = plugin.use_transformation_t2m(file)
        else:
            vm_temp = self.__transform_to_model_from_file(file)
            plugin = self.plugins.get_plugin_by_extension(
                vm_temp.get_extension())

            if operation_name not in self.get_name_operations_by_plugin(plugin.name):
                transformation_way = self.__search_transformation_way(
                    plugin, operation_name)

                for (_, dst) in transformation_way:
                    _plugin = self.plugins.get_plugin_by_extension(dst)
                    vm_temp = _plugin.use_transformation_m2m(vm_temp, dst)
                    plugin = _plugin

        operation = plugin.get_operation(operation_name)
        if isinstance(operation, OperationWithConfiguration):
            if configuration_file is None:
                raise ConfigurationNotFound()
            configuration = self.__transform_to_model_from_file(configuration_file)
            operation.set_configuration(configuration)

        operation = plugin.use_operation(operation, vm_temp)

        return operation.get_result()

    def __transform_to_model_from_file(self, file: str) -> VariabilityModel:
        t2m_transformations = self.get_transformations_t2m()
        extension = file.split('.')[-1]
        t2m_filters = filter(
            lambda t2m: t2m.get_source_extension() == extension,
            t2m_transformations
        )

        t2m = next(t2m_filters, None)
        if t2m is None:
            raise TransformationNotFound()

        return t2m(file).transform()

    def __search_transformation_way(
        self,
        plugin: Plugin,
        operation_name: str
    ) -> list[tuple[str, str]]:
        '''
        Search way to reach plugin with operation_name using m2m transformations
        '''
        way: list[tuple[str, str]] = []

        plugins_with_operation = self.get_plugins_with_operation(
            operation_name)
        m2m_transformations = self.get_transformations_m2m()

        input_extension = plugin.get_extension()

        def __search_recursive_way(
            input_extension: str,
            output_extension: str,
            tmp_way: list[tuple[str, str]]
        ) -> list[tuple[str, str]]:

            for m2m in m2m_transformations:
                in_m2m = m2m.get_source_extension()
                out_m2m = m2m.get_destination_extension()

                if out_m2m == output_extension:
                    _next = (in_m2m, out_m2m)

                    if _next in tmp_way:
                        continue

                    tmp_way.insert(0, _next)

                    if input_extension == in_m2m:
                        return tmp_way

                    return __search_recursive_way(input_extension, in_m2m, tmp_way)

            return tmp_way

        for _plugin in plugins_with_operation:
            output_extension = _plugin.get_extension()
            way = __search_recursive_way(input_extension, output_extension, [])
            if way and output_extension == way[-1][1]:
                return way

        raise NotImplementedError('Way to execute operation not found')