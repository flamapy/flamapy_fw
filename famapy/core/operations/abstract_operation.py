from abc import ABC, abstractmethod

from famapy.core.models import VariabilityModel


class Operation(ABC):

    @abstractmethod
    def execute(self, model: VariabilityModel) -> 'Operation':
        pass
