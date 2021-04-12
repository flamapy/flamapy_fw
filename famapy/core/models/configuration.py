from abc import ABC, abstractmethod

from famapy.core.models.variability_model import VariabilityModel


class Configuration(ABC):

    @abstractmethod
    def __init__(self, elements: dict[VariabilityModel, bool]) -> None:
        self.elements = elements
