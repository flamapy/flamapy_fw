from abc import abstractmethod
from typing import Optional

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation


class Sampling(Operation):
    """Sampling is the selection of a subset (i.e., a sample) of products
    (or configurations) from within a variability model.
    """

    @abstractmethod
    def sample(self, size: int, with_replacement: bool = False,
               partial_configuration: Optional[Configuration] = None) -> list[Configuration]:
        """Return a sample of configurations.

        Keyword arguments:
        size -- number of configurations of the sample.
        with_replacement -- allow repeated configurations in the sample (default False).
        partial_configuration -- from which the sample is built (default empty configuration).
        """
