from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation


class SatisfiableConfiguration(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration, is_full: bool) -> None:
        pass

    @abstractmethod
    def is_satisfiable(self) -> bool:
        pass
