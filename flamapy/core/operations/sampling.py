from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input


class Sampling(Operation):
    """Sampling is the selection of a subset (i.e., a sample) of products
    (or configurations) from within a variability model.
    """

    facade = OperationDescriptor(
        doc=(
            'Returns a random sample of valid configurations of the given size. When\n'
            'with_replacement is True, the same configuration may appear more than once.\n'
            '\n'
            '``backend`` selects the analysis plugin; defaults to bdd. sat and bdd\n'
            'implement (deterministic/enumerating) sampling; "sharpsat" provides almost-\n'
            'uniform sampling via the optional flamapy-sharpsat plugin.'
        ),
        returns='Union[None, List[Configuration]]',
        name='sampling', operation='Sampling', default_backend='bdd',
        selectable_backend=True,
        inputs=(
            Input('size', int, required=True, setter='set_sample_size'),
            Input('with_replacement', bool, default=False, setter='set_with_replacement'),
        ),
    )

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
