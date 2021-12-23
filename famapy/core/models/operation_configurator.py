import csv

from typing import Type, Any, Tuple

from famapy.core.exceptions import OperationNotFound
from famapy.core.models.configuration import Configuration
from famapy.core.models.variability_model import VariabilityModel
from famapy.core.operations import (Commonality, Filter, Sampling,
                                    ValidConfiguration, ValidProduct)
from famapy.core.utils import file_exists
from famapy.core.operations import Operation


class OperationConfigurator():

    def __init__(self, operation: Type[Operation], model: VariabilityModel) -> None:
        self.operation = operation
        self.model = model
        self.configuration: Configuration = Configuration({})

    def configure_from_csv(self) -> Operation:

        operation = self.operation

        # Sample feature class for operations expecting a .name from a feature
        class SampleFeature():
            def __init__(self, name: str) -> None:
                self.name = name

        # Behavior for every different operation
        if issubclass(operation, (ValidProduct)):
            valid_product = operation()
            csvreader = self.get_configuration_from_csv("valid_product.csv")
            elements = {}
            for row in csvreader:
                elements[SampleFeature(row[0])] = True
            valid_product.set_configuration(Configuration(elements))

            return valid_product

        if issubclass(operation, (ValidConfiguration)):
            valid_configuration = operation()
            csvreader = self.get_configuration_from_csv(
                "valid_configuration.csv")
            elements = {}
            for row in csvreader:
                elements[SampleFeature(row[0])] = (row[1] == "True")
            valid_configuration.set_configuration(Configuration(elements))

            return valid_configuration

        raise OperationNotFound

    @classmethod
    def get_configuration_from_csv(cls, path: str) -> list[list[str]]:
        # Returns a list of list
        if not file_exists(path):
            raise FileNotFoundError

        with open(path, 'r', encoding='utf-8') as csvfile:
            csvreader = list(csv.reader(csvfile))

        return csvreader

    @classmethod
    def get_configurable_operations(cls) -> Tuple[Any, ...]:
        # Every configurable operation to be supported must be added here
        return (Commonality, Filter, Sampling, ValidConfiguration, ValidProduct)

    def is_operation_configurable(self) -> bool:
        return issubclass(self.operation, self.get_configurable_operations())
