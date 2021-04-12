from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class FalseOptionalFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_false_optional_features(self) -> list[Any]:
        pass
