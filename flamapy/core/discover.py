import inspect
import logging
import warnings
from importlib import import_module
from importlib.metadata import EntryPoint, entry_points as metadata_entry_points
from pkgutil import iter_modules
from types import ModuleType
from typing import Any, Iterable, Optional, Protocol, Type, runtime_checkable, cast

from flamapy.core.config import PLUGIN_PATHS
from flamapy.core.exceptions import OperationNotFound
from flamapy.core.exceptions import TransformationNotFound
from flamapy.core.exceptions import ConfigurationNotFound
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, collect_descriptors
from flamapy.core.plugins import Operations, Plugin, Plugins
from flamapy.core.transformations import Transformation
from flamapy.core.transformations.text_to_model import TextToModel
from flamapy.core.transformations.model_to_model import ModelToModel
from flamapy.core.utils import filename_matches_extension
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


LOGGER = logging.getLogger("discover")

# Plugins declare themselves via an entry point in this group whose value is the metamodel
# package (e.g. ``pysat = "flamapy.metamodels.pysat_metamodel"``). The namespace scan over
# PLUGIN_PATHS is kept as a fallback for plugins that predate entry points; it will be removed
# in flamapy 3.1.
ENTRY_POINT_GROUP = "flamapy.plugins"


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
            LOGGER.exception("ModuleNotFoundError %s", path)
    return results


class DiscoverMetamodels:
    """Discovers installed plugins, preferring ``flamapy.plugins`` entry points.

    Plugins without an entry point are still found through the legacy namespace scan over
    ``PLUGIN_PATHS`` (with a DeprecationWarning — the scan is removed in flamapy 3.1). Passing
    ``entry_points`` explicitly takes full control of discovery (no scan), which is how tests
    inject synthetic plugins.
    """

    _instance: Optional["DiscoverMetamodels"] = None

    def __init__(self, entry_points: Optional[Iterable[EntryPoint]] = None) -> None:
        self._injected_entry_points = (
            list(entry_points) if entry_points is not None else None
        )
        self.plugins: Plugins = self.discover()

    @classmethod
    def instance(cls) -> "DiscoverMetamodels":
        """A process-wide shared instance, avoiding redundant discovery scans."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search_classes(self, module: ModuleType) -> list[Any]:
        classes = []
        for _, file_name, ispkg in iter_modules(module.__path__, module.__name__ + "."):
            if ispkg:
                classes += self.search_classes(import_module(file_name))
            else:
                _file = import_module(file_name)
                classes += [
                    member
                    for member in inspect.getmembers(_file, inspect.isclass)
                    if member[1].__module__ == _file.__name__
                ]

        return classes

    def _build_plugin(self, module: ModuleType) -> Plugin:
        plugin = Plugin(module=module)
        for _, _class in self.search_classes(module):
            if not _class.__module__.startswith(module.__package__):
                continue  # Exclude modules not in current package
            inherit = _class.mro()

            if Operation in inherit:
                plugin.append_operation(_class)
            elif Transformation in inherit:
                plugin.append_transformations(_class)
            elif VariabilityModel in inherit:
                plugin.variability_model = _class
        return plugin

    def discover(self) -> Plugins:
        plugins = Plugins()
        covered_modules: set[str] = set()

        if self._injected_entry_points is not None:
            found_entry_points: list[EntryPoint] = self._injected_entry_points
        else:
            found_entry_points = list(metadata_entry_points(group=ENTRY_POINT_GROUP))

        for entry_point in found_entry_points:
            try:
                module = entry_point.load()
            except Exception:  # pylint: disable=broad-except
                # The distribution is installed but its package is not importable in this
                # environment (e.g. a shadowed namespace during another package's test run).
                LOGGER.exception(
                    "Could not load plugin entry point %s=%s", entry_point.name,
                    entry_point.value)
                continue
            if module.__name__ in covered_modules:
                continue
            covered_modules.add(module.__name__)
            plugins.append(self._build_plugin(module))

        if self._injected_entry_points is not None:
            return plugins

        scan_only: list[str] = []
        for pkg in filter_modules_from_plugin_paths():
            for _, plugin_name, ispkg in iter_modules(pkg.__path__, pkg.__name__ + "."):
                if not ispkg or plugin_name in covered_modules:
                    continue
                module = import_module(plugin_name)
                covered_modules.add(plugin_name)
                plugins.append(self._build_plugin(module))
                scan_only.append(plugin_name)

        if scan_only:
            warnings.warn(
                f"Plugins discovered via the namespace scan without a '{ENTRY_POINT_GROUP}' "
                f"entry point: {', '.join(sorted(scan_only))}. Declare the entry point in the "
                "plugin's packaging metadata; the namespace-scan fallback will be removed in "
                "flamapy 3.1.",
                DeprecationWarning, stacklevel=2)
        return plugins

    def reload(self) -> None:
        self.plugins = self.discover()

    def get_operations(self) -> list[Type[Operation]]:
        """Get the operations for all modules"""
        operations: list[Type[Operation]] = []
        for plugin in self.plugins:
            operations += plugin.operations
        return operations

    def get_name_operations(self) -> list[str]:
        operations = []
        for operation in self.get_operations():
            operations.append(operation.__name__)
            base = operation.__base__.__name__ if operation.__base__ else ""
            if base != "ABC":
                operations.append(base)

        return operations

    def available_operations(self) -> dict[str, OperationDescriptor]:
        """Facade descriptors of every discovered operation that declares one, keyed by public name.

        This is the single source the facade, CLI and REST derive their operation surface from.
        """
        return collect_descriptors(self.get_operations())

    def get_transformations(self) -> list[Type[Transformation]]:
        """Get transformations for all modules"""
        transformations: list[Type[Transformation]] = []
        for plugin in self.plugins:
            transformations += plugin.transformations
        return transformations

    def get_transformations_t2m(self) -> list[Type[TextToModel]]:
        """Get t2m transformations for all modules"""

        transformations: list[Type[TextToModel]] = []
        for plugin in self.plugins:
            transformations += [t for t in plugin.transformations if issubclass(t, TextToModel)]
        return transformations

    def get_transformations_m2m(self) -> list[Type[ModelToModel]]:
        """Get m2m transformations for all modules"""

        transformations: list[Type[ModelToModel]] = []
        for plugin in self.plugins:
            transformations += [t for t in plugin.transformations if issubclass(t, ModelToModel)]
        return transformations

    def get_operations_by_plugin(self, plugin_name: str) -> Operations:
        return self.plugins.get_operations_by_plugin_name(plugin_name)

    def get_plugins_with_operation(self, operation_name: str) -> list[Plugin]:
        return [
            plugin
            for plugin in self.plugins
            if operation_name in self.get_name_operations_by_plugin(plugin.name)
        ]

    def get_name_operations_by_plugin(self, plugin_name: str) -> list[str]:
        operations = []
        for operation in self.get_operations_by_plugin(plugin_name):
            operations.append(operation.__name__)
            base = operation.__base__.__name__ if operation.__base__ else ""
            if base != "ABC":
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

    def get_operation(self, src: VariabilityModel, operation_name: str) -> Operation:
        plugin = self.plugins.get_plugin_by_variability_model(src)
        return plugin.get_operation(operation_name)

    def use_operation(self, src: VariabilityModel, operation_name: str) -> Operation:
        plugin = self.plugins.get_plugin_by_variability_model(src)
        operation = plugin.get_operation(operation_name)
        return plugin.use_operation(operation, src)

    # pylint: disable=too-many-arguments
    def use_operation_from_vm(
        self,
        operation_name: str,
        vm_orig: VariabilityModel,
        plugin_name: Optional[str] = None,
        configuration_file: Optional[str] = None,
        is_full: Optional[bool] = False,
    ) -> Any:
        if operation_name not in self.get_name_operations():
            raise OperationNotFound()
        vm_temp = vm_orig
        if plugin_name is not None:
            plugin = self.plugins.get_plugin_by_name(plugin_name)
            # vm_temp = plugin.use_transformation_t2m(file)
        else:
            # vm_temp = self.__transform_to_model_from_file(file)
            plugin = self.plugins.get_plugin_by_extension(vm_orig.get_extension())

            if operation_name not in self.get_name_operations_by_plugin(plugin.name):
                transformation_way = self.__search_transformation_way(plugin, operation_name)

                for _, dst in transformation_way:
                    _plugin = self.plugins.get_plugin_by_extension(dst)
                    vm_temp = _plugin.use_transformation_m2m(vm_temp, dst)
                    plugin = _plugin

        operation = plugin.get_operation(operation_name)
        if isinstance(operation, OperationWithConfiguration):
            if configuration_file is None:
                raise ConfigurationNotFound()
            configuration = self.__transform_to_model_from_file(configuration_file)
            configuration = cast(Configuration, configuration)
            is_full_value = is_full if is_full is not None else False
            configuration.set_full(is_full_value)
            operation.set_configuration(configuration)

        operation = plugin.use_operation(operation, vm_temp)

        return operation.get_result()

    # pylint: disable=too-many-arguments
    def use_operation_from_file(
        self,
        operation_name: str,
        file: str,
        plugin_name: Optional[str] = None,
        configuration_file: Optional[str] = None,
        is_full: Optional[bool] = False,
    ) -> Any:
        if operation_name not in self.get_name_operations():
            raise OperationNotFound()

        if plugin_name is not None:
            plugin = self.plugins.get_plugin_by_name(plugin_name)
            vm_temp = plugin.use_transformation_t2m(file)
        else:
            vm_temp = self.__transform_to_model_from_file(file)
            plugin = self.plugins.get_plugin_by_extension(vm_temp.get_extension())

            if operation_name not in self.get_name_operations_by_plugin(plugin.name):
                transformation_way = self.__search_transformation_way(plugin, operation_name)

                for _, dst in transformation_way:
                    _plugin = self.plugins.get_plugin_by_extension(dst)
                    vm_temp = _plugin.use_transformation_m2m(vm_temp, dst)
                    plugin = _plugin

        operation = plugin.get_operation(operation_name)
        if isinstance(operation, OperationWithConfiguration):
            if configuration_file is None:
                raise ConfigurationNotFound()
            configuration = self.__transform_to_model_from_file(configuration_file)
            configuration = cast(Configuration, configuration)
            is_full_value = is_full if is_full is not None else False
            configuration.set_full(is_full_value)
            operation.set_configuration(configuration)

        operation = plugin.use_operation(operation, vm_temp)
        return operation.get_result()

    def __transform_to_model_from_file(self, file: str) -> VariabilityModel:
        t2m_transformations = self.get_transformations_t2m()
        # Prefer the most specific matching extension (e.g. 'uvl.json' over 'json').
        candidates = [
            t2m
            for t2m in t2m_transformations
            if filename_matches_extension(file, t2m.get_source_extension())
        ]
        if not candidates:
            raise TransformationNotFound()
        t2m = max(candidates, key=lambda t: len(t.get_source_extension()))

        return t2m(file).transform()

    def __search_transformation_way(
        self, plugin: Plugin, operation_name: str
    ) -> list[tuple[str, str]]:
        """
        Search way to reach plugin with operation_name using m2m transformations
        """
        way: list[tuple[str, str]] = []

        plugins_with_operation = self.get_plugins_with_operation(operation_name)
        m2m_transformations = self.get_transformations_m2m()

        input_extension = plugin.get_extension()

        def __search_recursive_way(
            input_extension: str, output_extension: str, tmp_way: list[tuple[str, str]]
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

        raise NotImplementedError("Way to execute operation not found")
