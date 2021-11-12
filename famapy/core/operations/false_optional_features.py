from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class FalseOptionalFeatures(Operation):
    """A feature is `false optional` if it is included in all the products of the variability model 
    despite not being modeled as mandatory.

    The definition of `optional feature` varies in the literature.
    For instance, in [Batory2005 @ SPLC - https://link.springer.com/chapter/10.1007%2F11554844_3]
    a feature is optional if it can be selected and deselected, while in 
    FeatureIDE [https://doi.org/10.1016/j.scico.2012.06.002] a feature is optional if it can be 
    deselected when its parent in the feature diagram representation is selected. 
    
    Given a subset of features marked as optional (this includes optional features as well as 
    features in or-groups and feature in alternative-groups),
    the false optional features analysis retrieves all the false optional ones.

    In general, false optional should be marked as mandatory for maintainability purposes.
    """

    @abstractmethod
    def get_false_optional_features(self, optional_features: list[Any]) -> list[Any]:
        pass
