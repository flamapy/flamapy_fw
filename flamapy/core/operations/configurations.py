from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class Configurations(Operation):
    facade = OperationDescriptor(
        doc=(
            'These are the individual outcomes that can be produced from a feature model.\n'
            'Each product is a combination of features that satisfies all the constraints\n'
            'and dependencies in the feature model.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd" or "z3"); defaults to\n'
            'bdd.'
        ),
        returns='Union[None, List[Configuration]]',
        name='configurations', operation='Configurations', default_backend='bdd',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations(self) -> list[Configuration]:
        pass
