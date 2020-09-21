from abc import abstractmethod

from famapy.core.models import Configuration
from famapy.core.operations import Operation


class Commonality(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration):
        pass

    @abstractmethod
    def get_commonality(self) -> float:
        pass
