from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.models.variability_model import VariabilityElement


class DeadFeatures(Operation):
    facade = OperationDescriptor(
        name='dead_features', operation='DeadFeatures', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_dead_features(self) -> list[VariabilityElement]:
        pass
