from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class CoreFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_core_features(self) -> list[Any]:
        pass
