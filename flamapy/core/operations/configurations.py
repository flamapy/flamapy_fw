from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class Configurations(Operation):
    facade = OperationDescriptor(
        name='configurations', operation='Configurations', default_backend='bdd'
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations(self) -> list[Configuration]:
        pass
