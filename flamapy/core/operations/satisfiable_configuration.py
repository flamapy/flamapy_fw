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
