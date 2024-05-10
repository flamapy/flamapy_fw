from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation
from flamapy.core.models.variability_model import VariabilityElement

class CoreFeatures(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_core_features(self) -> list[VariabilityElement]:
        pass
