from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.models.variability_model import VariabilityElement


class FalseOptionalFeatures(Operation):
    """A feature is defined as `false optional` if the selection of its parent makes the feature
    itself selected as well, although it is defined as optional and not mandatory.

    A feature in a group can be also `false optional`.
    In general, false optional features should be marked as mandatory for maintainability purposes.
    """

    facade = OperationDescriptor(
        doc=(
            'These are features that appear to be optional in the feature model, but due to\n'
            'the constraints and dependencies, must be included in every valid product.\n'
            'Like dead features, false optional features are usually a sign of an error in\n'
            'the feature model.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd" or "z3"); defaults to\n'
            'sat.'
        ),
        returns='Union[None, List[str]]',
        name='false_optional_features', operation='FalseOptionalFeatures', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def get_false_optional_features(self) -> list[VariabilityElement]:
        pass
