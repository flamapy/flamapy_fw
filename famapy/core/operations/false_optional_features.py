from abc import abstractmethod

from famapy.core.operations import Operation


class FalseOptionalFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_false_optional_features(self) -> list:
        pass

    @abstractmethod
    def set_core_features(self, core_features: list):
        pass
