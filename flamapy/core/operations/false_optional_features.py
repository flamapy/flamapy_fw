from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class FalseOptionalFeatures(Operation):
    """A feature is defined as `false optional` if the selection of its parent makes the feature
    itself selected as well, although it is defined as optional and not mandatory.

    A feature in a group can be also `false optional`.
    In general, false optional features should be marked as mandatory for maintainability purposes.
    """

    @abstractmethod
    def get_false_optional_features(self) -> list[Any]:
        pass
