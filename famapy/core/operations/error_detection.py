from abc import abstractmethod

from famapy.core.operations import Operation


class ErrorDetection(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_errors_messages(self) -> list:
        pass

    @abstractmethod
    def set_dead_features(self, dead_features: list):
        pass

    @abstractmethod
    def set_false_optional_features(self, false_optional_features: list):
        pass
