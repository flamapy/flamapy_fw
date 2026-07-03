from abc import abstractmethod
from enum import Enum
from typing import Any

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input


class OptimizationGoal(Enum):
    MAXIMIZE = 'Maximize'
    MINIMIZE = 'Minimize'


def _attribute_optimization_inputs(operation: Any, facade: Any, kwargs: dict[str, Any]) -> None:
    objectives = kwargs['objectives']
    if isinstance(objectives, str):
        attributes = {objectives: OptimizationGoal.MINIMIZE}
    else:
        attributes = {
            name: (OptimizationGoal.MINIMIZE if str(goal).lower().startswith('min')
                   else OptimizationGoal.MAXIMIZE)
            for name, goal in dict(objectives).items()
        }
    operation.set_attributes(attributes)


def _attribute_optimization_result(result: Any) -> Any:
    # z3 returns (configuration, values) tuples; sat returns bare configurations.
    return [item[0] if isinstance(item, tuple) else item for item in result]


class AttributeOptimization(Operation):
    """Return the configuration(s) that optimize the given numeric feature attribute(s).

    Attributes are identified by name and mapped to an :class:`OptimizationGoal`. The
    objective for each attribute is the sum of its values over the selected features.
    """

    facade = OperationDescriptor(
        doc=(
            'Returns the configuration(s) that optimize one or more numeric feature\n'
            'attributes.\n'
            '\n'
            '``objectives`` is either a single attribute name (defaults to minimizing it)\n'
            'or a mapping ``{attribute_name: "Minimize"|"Maximize"}``. ``backend`` selects\n'
            'the plugin: "sat" performs single-objective MaxSAT optimization; "z3"\n'
            'additionally supports typed attributes and multi-objective (Pareto)\n'
            'optimization. Defaults to "sat".'
        ),
        returns='Union[None, List[Configuration]]',
        name='attribute_optimization', operation='AttributeOptimization', default_backend='sat',
        selectable_backend=True,
        inputs=(Input('objectives', Any, required=True),),
        input_adapter=_attribute_optimization_inputs,
        result_adapter=_attribute_optimization_result,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_attributes(self, attributes: dict[str, OptimizationGoal]) -> None:
        """Set the attributes to optimize as a mapping ``{attribute_name: OptimizationGoal}``."""

    @abstractmethod
    def optimize(self) -> list[Any]:
        """Return the optimal configuration(s)."""
