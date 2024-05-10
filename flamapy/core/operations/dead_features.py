from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation
from flamapy.core.models.variability_model import VariabilityElement


class DeadFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_dead_features(self) -> list[VariabilityElement]:
        pass
