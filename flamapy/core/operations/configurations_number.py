from abc import abstractmethod

from flamapy.core.operations import Operation


class ConfigurationsNumber(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations_number(self) -> int:
        pass
