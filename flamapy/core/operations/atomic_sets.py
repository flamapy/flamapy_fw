from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor


def _atomic_sets_result(result: Any) -> Any:
    """The names of the features of each atomic set (the feature-model implementation returns
    Feature objects, the solver-based ones feature names)."""
    return [[getattr(feature, 'name', feature) for feature in atomic_set]
            for atomic_set in result]


class AtomicSets(Operation):
    """An atomic set is a group of features that can be treated as a unit when
    performing certain operations.

    The intuitive idea of atomic sets is that mandatory features and their parent features
    can be treated as a whole in certain analysis operation without altering the result.
    This is because those features can never appear in a product separately.

    The exact definition: two features belong to the same atomic set when every configuration
    of the model selects both or neither, so each set is a class of features with the same
    value in every configuration. The feature-model implementation reads only the tree
    (mandatory children with their parents) and ignores the cross-tree constraints, which can
    merge sets; the solver-based implementations compute the classes exactly.
    """

    facade = OperationDescriptor(
        doc=(
            'This operation is used to find the atomic sets in a model: It returns the\n'
            'atomic sets if they are found in the model. If the model does not follow the\n'
            'UVL specification, an exception is raised and the operation returns False.\n'
            '\n'
            'By default the sets are read from the feature tree (mandatory features with\n'
            'their parents), ignoring the cross-tree constraints; ``backend="sat"`` computes\n'
            'the exact sets, the classes of features that every configuration selects\n'
            'together.'
        ),
        returns='Union[None, List[List[Any]]]',
        name='atomic_sets', operation='AtomicSets', selectable_backend=True,
        result_adapter=_atomic_sets_result,
    )

    @abstractmethod
    def atomic_sets(self) -> list[set[Any]]:
        """Return a list of atomic sets of the feature model."""
