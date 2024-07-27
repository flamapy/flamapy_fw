from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation


class Sampling(Operation):
    """Sampling is the selection of a subset (i.e., a sample) of products
    (or configurations) from within a variability model.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_sample_size(self, sample_size: int) -> None:
        """Number of configurations of the sample."""

    @abstractmethod
    def set_with_replacement(self, with_replacement: bool) -> None:
        "Allow repeated configurations in the sample (default False)."

    @abstractmethod
    def set_partial_configuration(self, partial_configuration: Configuration) -> None:
        "From which the sample is built (default empty configuration)."

    @abstractmethod
    def get_sample(self) -> list[Configuration]:
        """Return a sample of configurations."""
