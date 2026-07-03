from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor


class ConfigurationsNumber(Operation):
    facade = OperationDescriptor(
        name='configurations_number', operation='ConfigurationsNumber', default_backend='bdd',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations_number(self) -> int:
        pass
