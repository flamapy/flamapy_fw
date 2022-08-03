from abc import ABC, abstractmethod
from typing import Any

from flamapy.core.models import VariabilityModel


class Operation(ABC):

    @abstractmethod
    def execute(self, model: VariabilityModel) -> 'Operation':
        pass

    @abstractmethod
    def get_result(self) -> Any:
        pass
