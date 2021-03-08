from abc import ABC, abstractmethod
from typing import Any

from famapy.core.models import VariabilityModel


class Operation(ABC):

    @classmethod
    def get_parent_name(cls) -> str:
        return 'Operation'

    @abstractmethod
    def execute(self, model: VariabilityModel) -> 'Operation':
        pass

    @abstractmethod
    def get_result(self) -> Any:
        pass
