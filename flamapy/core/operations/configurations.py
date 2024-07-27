from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class Configurations(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations(self) -> list[Configuration]:
        pass
