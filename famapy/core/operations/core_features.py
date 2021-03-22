from abc import abstractmethod

from famapy.core.operations import Operation


class CoreFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_core_features(self) -> list:
        pass
