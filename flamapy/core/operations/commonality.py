from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation


class Commonality(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def get_commonality(self) -> float:
        pass
