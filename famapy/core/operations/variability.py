from abc import abstractmethod

from famapy.core.operations import Operation


class Variability(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_variability(self) -> float:
        pass
