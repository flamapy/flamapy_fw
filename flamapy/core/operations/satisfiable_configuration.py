from abc import abstractmethod
from typing import Any

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input


def _satisfiable_configuration_inputs(operation: Any, facade: Any, kwargs: dict[str, Any]) -> None:
    configuration = facade._as_configuration(kwargs['configuration_path'])
    configuration.is_full = bool(kwargs.get('full_configuration', False))
    operation.set_configuration(configuration)


class SatisfiableConfiguration(Operation):
    facade = OperationDescriptor(
        doc=(
            'This is a product that is produced from a valid configuration of features. A\n'
            'valid product satisfies all the constraints and dependencies in the feature\n'
            'model.\n'
            '\n'
            '``configuration_path`` accepts a configuration file path, a ``{feature:\n'
            'value}`` mapping, or a Configuration object. ``backend`` selects the analysis\n'
            'plugin ("sat", "bdd" or "z3"); defaults to sat.'
        ),
        returns='Union[None, bool]',
        name='satisfiable_configuration', operation='SatisfiableConfiguration',
        default_backend='sat', selectable_backend=True,
        inputs=(
            Input('configuration_path', str, required=True, kind='configuration',
                  setter='set_configuration'),
            Input('full_configuration', bool, default=False),
        ),
        input_adapter=_satisfiable_configuration_inputs,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def is_satisfiable(self) -> bool:
        pass
