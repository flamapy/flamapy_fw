from abc import abstractmethod
from famapy.core.operations import Operation


class CoreFeatures(Operation):
    """
    This operation takes a feature model as input
    and returns the set of features that are part of all the products
    in the software product line.

    Core features are the most relevant features of the software product line
    since they are supposed to appear in all products.
    Hence, this operation is useful to determine which features
    should be developed in first place or to decide which features
    should be part of the core architecture of the software product line.

    Ref. Benavides2010 [IS] - Automated analysis of feature models 20 years later: A literature review
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_core_features(self) -> list:
        pass
