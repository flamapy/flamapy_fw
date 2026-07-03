from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor


class Satisfiable(Operation):
    facade = OperationDescriptor(
        name='satisfiable', operation='Satisfiable', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def is_satisfiable(self) -> bool:
        pass
