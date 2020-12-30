from types import FunctionType, ModuleType
from typing import List
from collections import UserList

from famapy.core.exceptions import (
    OperationNotFound,
    PluginNotFound,
    TransformationNotFound,
)
from famapy.core.models import VariabilityModel
from famapy.core.operations import Operation
from famapy.core.transformations import (
    TextToModel,
    Transformation,
    ModelToText,
    ModelToModel,
)
from famapy.core.utils import extract_filename_extension


class Transformations(UserList):  # pylint: disable=too-many-ancestors
    data: List[Transformation]


class Operations(UserList):  # pylint: disable=too-many-ancestors
    data: List[Operation]

    def search_by_name(self, name: str) -> Operation:
#       This has been modified to use the parent class name 
#       candidates = filter(lambda op: op.__name__ == name, self.data)
        candidates = filter(lambda op: op.__base__.__name__ == name, self.data)
        try:
            operation = next(candidates, None)
        except StopIteration:
            raise OperationNotFound
        return operation


class Plugin:

    def __init__(self, module: ModuleType) -> None:
        self.module: ModuleType = module
        self.variability_model: VariabilityModel = None
        self.operations: Operations = Operations()
        self.transformations: Transformations = Transformations()

    def __get_transformation(
        self,
        filter_transformation: FunctionType
    ) -> Transformation:
        candidates = filter(filter_transformation, self.transformations)
        try:
            transformation = next(candidates, None)
        except StopIteration:
            raise TransformationNotFound
        return transformation

    def append_operation(self, operation: Operation) -> None:
        self.operations.append(operation)

    def append_transformations(self, transformation: Transformation) -> None:
        self.transformations.append(transformation)

    def use_operation(self, name: str, src: VariabilityModel) -> Operation:
        operation = self.operations.search_by_name(name)
        return operation().execute(model=src)

    def use_transformation_t2m(self, src: str) -> VariabilityModel:
        extension = extract_filename_extension(src)

        def filter_transformations(transformation):
            return TextToModel in transformation.mro() and\
                transformation.get_source_extension() == extension

        transformation = self.__get_transformation(filter_transformations)
        result = transformation(src)
        return result.transform()

    def use_transformation_m2t(self, src: VariabilityModel, dst: str) -> str:
        extension = extract_filename_extension(dst)

        def filter_transformations(transformation):
            return ModelToText in transformation.mro() and\
                transformation.get_destination_extension() == extension

        transformation = self.__get_transformation(filter_transformations)
        result = transformation(src, dst)
        return result.transform()

    def use_transformation_m2m(
        self,
        src: VariabilityModel,
        dst: str
    ) -> VariabilityModel:
        def filter_transformations(transformation):
            return ModelToModel in transformation.mro() and\
                transformation.get_destination_extension() == dst and\
                transformation.get_source_extension() == src.get_extension()

        transformation = self.__get_transformation(filter_transformations)
        result = transformation(src)
        return result.transform()

    def get_extension(self):
        return self.variability_model.get_extension()

    @property
    def name(self):
        return self.module.__name__.split('.')[-1]

    def get_stats(self):
        return {
            'amount_operations': len(self.operations),
            'amount_transformations': len(self.transformations),
            'variability_model': bool(self.variability_model)
        }


class Plugins(UserList):  # pylint: disable=too-many-ancestors
    data: List[Plugin]

    def __get_plugin_by_filter(self, plugin_filter: FunctionType):
        candidates = filter(plugin_filter, self.data)
        try:
            plugin = next(candidates)
        except StopIteration:
            raise PluginNotFound
        return plugin

    def get_plugin_by_name(self, name: str):

        def plugin_filter(plugin):
            return plugin.name == name

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_by_variability_model(
        self,
        variability_model: VariabilityModel
    ) -> Plugin:

        def plugin_filter(plugin):
            return isinstance(variability_model, plugin.variability_model)

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_by_extension(self, extension: str) -> Plugin:

        def plugin_filter(plugin):
            return extension == plugin.get_extension()

        return self.__get_plugin_by_filter(plugin_filter)

    def get_plugin_names(self) -> List[str]:
        return [plugin.name for plugin in self.data]

    def get_variability_models(self) -> List[VariabilityModel]:
        return [plugin.variability_model for plugin in self.data]

    def get_operations_by_plugin_name(self, plugin_name: str) -> Operations:
        try:
            plugin = self.get_plugin_by_name(plugin_name)
            return plugin.operations
        except PluginNotFound:
            return Operations()

    def get_stats(self):
        stats = {'amount_plugins': len(self.data)}
        for plugin in self.data:
            stats[plugin.name] = plugin.get_stats()
        return stats
