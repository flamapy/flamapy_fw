from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor


class Satisfiable(Operation):
    facade = OperationDescriptor(
        doc=(
            'In the context of feature models, this usually refers to whether the feature\n'
            'model itself satisfies all the constraints and dependencies. A a valid feature\n'
            'model is one that does encodes at least a single valid product.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd" or "z3"); defaults to\n'
            'sat.'
        ),
        returns='Union[None, bool]',
        name='satisfiable', operation='Satisfiable', default_backend='sat',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def is_satisfiable(self) -> bool:
        pass
