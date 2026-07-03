from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.models.variability_model import VariabilityElement


class CoreFeatures(Operation):
    facade = OperationDescriptor(
        doc=(
            'These are the features that are present in all products of a product line. In\n'
            'a feature model, they are the features that are mandatory and not optional.\n'
            'Core features define the commonality among all products in a product line.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd" or "z3"); defaults to\n'
            'sat.'
        ),
        returns='Union[None, List[str]]',
        name='core_features', operation='CoreFeatures', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_core_features(self) -> list[VariabilityElement]:
        pass
