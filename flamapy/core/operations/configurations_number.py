from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor


class ConfigurationsNumber(Operation):
    facade = OperationDescriptor(
        doc=(
            'This is the total number of different full configurations that can be produced\n'
            "from a feature model. It's calculated by considering all possible combinations\n"
            'of features, taking into account the constraints and dependencies between\n'
            'features.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat", "bdd", "z3", or "sharpsat" for\n'
            'a scalable approximate count via the optional flamapy-sharpsat plugin);\n'
            'defaults to bdd.'
        ),
        returns='Union[None, int]',
        name='configurations_number', operation='ConfigurationsNumber', default_backend='bdd',
        selectable_backend=True,
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_configurations_number(self) -> int:
        pass
