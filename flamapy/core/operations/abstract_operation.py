from abc import ABC, abstractmethod
from typing import Any

from flamapy.core.models import VariabilityModel


class Operation(ABC):
    # Whether results are exact. Approximate/estimating implementations (e.g. sharpsat
    # counting, fm's estimated configurations number) override this with False; the value
    # is reported in the OperationResult envelope (see flamapy.core.execution).
    exact: bool = True

    @abstractmethod
    def execute(self, model: VariabilityModel) -> "Operation":
        pass

    @abstractmethod
    def get_result(self) -> Any:
        pass
