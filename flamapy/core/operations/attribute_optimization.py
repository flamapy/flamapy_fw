from abc import abstractmethod
from enum import Enum
from typing import Any

from flamapy.core.operations import Operation


class OptimizationGoal(Enum):
    MAXIMIZE = 'Maximize'
    MINIMIZE = 'Minimize'


class AttributeOptimization(Operation):
    """Return the configuration(s) that optimize the given numeric feature attribute(s).

    Attributes are identified by name and mapped to an :class:`OptimizationGoal`. The
    objective for each attribute is the sum of its values over the selected features.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_attributes(self, attributes: dict[str, OptimizationGoal]) -> None:
        """Set the attributes to optimize as a mapping ``{attribute_name: OptimizationGoal}``."""

    @abstractmethod
    def optimize(self) -> list[Any]:
        """Return the optimal configuration(s)."""
