from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class DeadFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_dead_features(self) -> list[Any]:
        pass
