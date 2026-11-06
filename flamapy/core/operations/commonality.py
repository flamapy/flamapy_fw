from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import Input, OperationDescriptor


class Commonality(Operation):
    """The commonality of a (partial) configuration: the fraction of the configurations of the
    model that include it, i.e. that select every feature it selects and deselect every feature
    it deselects (0 on a void model). With a single selected feature it is the feature's
    commonality factor: 1 for a core feature, 0 for a dead one, and the mean over the features
    is the homogeneity of the model.

    Ref.: Durán et al. 2017. FLAME: a formal framework for the automated analysis of software
    product lines validated by automated specification testing
    (https://doi.org/10.1007/s10270-015-0503-z).
    """

    facade = OperationDescriptor(
        doc=(
            'This is a measure of how often a feature appears in the products of a product\n'
            "line. It's usually expressed as a percentage. A feature with 100 per cent\n"
            'commonality is a core feature, as it appears in all products. With a partial\n'
            'configuration, it is the fraction of the products that include it (select\n'
            'every feature it selects and none of the features it deselects).\n'
            '\n'
            '``configuration_path`` accepts a configuration file path, a ``{feature:\n'
            'value}`` mapping, or a Configuration object.\n'
            '\n'
            '``backend`` selects the analysis plugin ("sat" enumerates the products, "bdd"\n'
            'counts them on the compiled BDD); defaults to sat.'
        ),
        returns='Union[None, float]',
        name='commonality', operation='Commonality', default_backend='sat',
        selectable_backend=True,
        inputs=(Input('configuration_path', str, required=True, kind='configuration',
                      setter='set_configuration'),),
    )

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def get_commonality(self) -> float:
        pass
