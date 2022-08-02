from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class AtomicSets(Operation):
    """An atomic set is a group of features that can be treated as a unit when 
    performing certain operations.

    The intuitive idea of atomic sets is that mandatory features and their parent features 
    can be treated as a whole in certain analysis operation without altering the result. 
    This is because those features can never appear in a product separately.
    """

    @abstractmethod
    def atomic_sets(self) -> list[set[Any]]:
        """Return a list of atomic sets of the feature model."""  
