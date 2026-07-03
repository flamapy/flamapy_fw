from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.models.variability_model import VariabilityElement


class DeadFeatures(Operation):
    facade = OperationDescriptor(
        doc=(
            'These are features that, due to the constraints and dependencies in the\n'
            'feature model, cannot be included in any valid product. Dead features are\n'
            'usually a sign of an error in the feature model.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd" or "z3"); defaults to\n'
            'sat.'
        ),
        returns='Union[None, List[str]]',
        name='dead_features', operation='DeadFeatures', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_dead_features(self) -> list[VariabilityElement]:
        pass
