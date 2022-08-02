from types import ModuleType
from typing import Any, Callable, Type, cast
from collections import UserList

from flamapy.core.exceptions import (
    OperationNotFound,
    PluginNotFound,
    TransformationNotFound,
)
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.transformations import (
    TextToModel,
    Transformation,
    ModelToText,
    ModelToModel,
)
from flamapy.core.utils import extract_filename_extension


class Transformations(UserList[Type[Transformation]]):
    data: list[Type[Transformation]]


class Operations(UserList[Type[Operation]]):
    data: list[Type[Operation]]

    def search_by_name(self, name: str) -> Type[Operation]:
        candidates = filter(
            lambda op: name in [op.__name__, op.__base__.__name__],
            self.data
        )

        try:
            operation = next(candidates, None)
        except StopIteration:
            raise OperationNotFound from StopIteration
        else:
            if not operation:
                raise OperationNotFound
        return operation


class Plugin:

    def __init__(self, module: ModuleType) -> None:
        self.module: ModuleType = module
        self.variability_model: VariabilityModel = None  # type: ignore
        self.operations: Operations = Operations()
        self.transformations: Transformations = Transformations()

    def __get_transformation(
        self,
        filter_transformation: Callable[..., bool]
    ) -> Type[Transformation]:
        candidates = filter(filter_transformation, self.transformations)
        try:
            transformation = next(candidates, None)
        except StopIteration:
            raise TransformationNotFound from StopIteration
        else:
            if not transformation:
                raise TransformationNotFound
        return transformation

    def append_operation(self, operation: Type[Operation]) -> None:
        self.operations.append(operation)

    def append_transformations(self, transformation: Type[Transformation]) -> None:
        self.transformations.append(transformation)

    def get_operation(self, name: str) -> Operation:
        operation = self.operations.search_by_name(name)
        return operation()

    def use_operation(self, operation: Operation, src: VariabilityModel) -> Operation:
        return operation.execute(model=src)

    def use_transformation_t2m(self, src: str) -> VariabilityModel:
        extension = extract_filename_extension(src)

        def filter_transformations(transformation: Type[Transformation]) -> bool:
            return issubclass(transformation, TextToModel) and\
                transformation.get_source_extension() == extension

        transformation: Type[TextToModel] = cast(
            Type[TextToModel],
            self.__get_transformation(filter_transformations)
        )
        result = transformation(src)
        return result.transform()

    def use_transformation_m2t(self, src: VariabilityModel, dst: str) -> str:
        extension = extract_filename_extension(dst)

        def filter_transformations(transformation: Type[Transformation]) -> bool:
            return issubclass(transformation, ModelToText) and\
                transformation.get_destination_extension() == extension

        transformation: Type[ModelToText] = cast(
            Type[ModelToText],
            self.__get_transformation(filter_transformations)
        )
        result = transformation(path=dst, source_model=src)
        return result.transform()

    def use_transformation_m2m(
        self,
        src: VariabilityModel,
        dst: str
    ) -> VariabilityModel:
        def filter_transformations(transformation: Type[Transformation]) -> bool:
            return issubclass(transformation, ModelToModel) and\
                transformation.get_destination_extension() == dst and\
                transformation.get_source_extension() == src.get_extension()

        transformation: Type[ModelToModel] = cast(
            Type[ModelToModel],
            self.__get_transformation(filter_transformations)
        )
        result = transformation(src)
        return result.transform()

    def get_extension(self) -> str:
        return self.variability_model.get_extension()

    @property
    def name(self) -> str:
        return self.module.__name__.split('.')[-1]

    def get_stats(self) -> dict[str, Any]:
        return {
            'amount_operations': len(self.operations),
            'amount_transformations': len(self.transformations),
            'variability_model': bool(self.variability_model)
        }


class Plugins(UserList[Plugin]):
    data: list[Plugin]

    def __get_plugin_by_filter(self, plugin_filter: Callable[[Plugin], bool]) -> Plugin:
        candidates = filter(plugin_filter, self.data)
        try:
            plugin = next(candidates)
        except StopIteration:
            raise PluginNotFound from StopIteration
        return plugin

    def get_plugin_by_name(self, name: str) -> Plugin:

        def plugin_filter(plugin: Plugin) -> bool:
            return plugin.name == name

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_by_variability_model(
        self,
        variability_model: VariabilityModel
    ) -> Plugin:

        def plugin_filter(plugin: Plugin) -> bool:

            return isinstance(variability_model,
                              plugin.variability_model)  # type: ignore
            # TODO: Check if this error can be ignored

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_by_extension(self, extension: str) -> Plugin:

        def plugin_filter(plugin: Plugin) -> bool:
            return extension == plugin.get_extension()

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_names(self) -> list[str]:
        return [plugin.name for plugin in self.data]

    def get_variability_models(self) -> list[VariabilityModel]:
        return [plugin.variability_model for plugin in self.data]

    def get_operations_by_plugin_name(self, plugin_name: str) -> Operations:
        try:
            plugin = self.get_plugin_by_name(plugin_name)
            return plugin.operations
        except PluginNotFound:
            return Operations()

    def get_stats(self) -> dict[str, Any]:
        stats: dict[str, Any] = {'amount_plugins': len(self.data)}
        for plugin in self.data:
            stats[plugin.name] = plugin.get_stats()
        return stats
