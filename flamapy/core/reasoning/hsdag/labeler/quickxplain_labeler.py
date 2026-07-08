"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/labeler/QuickXPlainLabeler.java
"""

from dataclasses import dataclass
from typing import List

from .labeler import IHSLabelable, LabelerType, AbstractHSParameters
from ...protocols import ConsistencyChecker
from ...quickxplain import QuickXPlain


@dataclass
class QuickXPlainParameters(AbstractHSParameters):
    set_b: List[int]

    def __str__(self) -> str:
        return f"QuickXPlainParameters{{C={self.set_c}, B={self.set_b}}}"


class QuickXPlainLabeler(QuickXPlain, IHSLabelable):
    """
    HSLabeler for QuickXPlain algorithm
    """

    def __init__(self, checker: ConsistencyChecker, parameters: QuickXPlainParameters):
        super().__init__(checker)
        self.initial_parameters = parameters

    def get_type(self) -> LabelerType:
        return LabelerType.CONFLICT

    def get_initial_parameters(self) -> AbstractHSParameters:
        return self.initial_parameters

    def get_label(self, parameters: AbstractHSParameters) -> List[List[int]]:
        """
        Identifies a conflict
        """
        assert isinstance(parameters, QuickXPlainParameters), \
            "parameter must be an instance of QuickXPlainParameters"

        set_cs = self.find_conflict(parameters.set_c, parameters.set_b + parameters.set_d)

        if len(set_cs) != 0:
            # reverse the order of the conflict set
            set_cs.reverse()
            return [set_cs]
        return []

    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters,
                                     arc_label: int) -> AbstractHSParameters:
        """
        Identifies the new node's parameters on the basis of the parent node's parameters.
        """
        assert isinstance(param_parent_node, QuickXPlainParameters), \
            "parameter must be an instance of QuickXPlainParameters"

        new_c = param_parent_node.set_c.copy()
        new_c.remove(arc_label)
        new_b = param_parent_node.set_b.copy()
        new_d = param_parent_node.set_d.copy()
        new_d.append(-1 * arc_label)

        return QuickXPlainParameters(new_c, new_d, new_b)

    def get_instance(self, checker: ConsistencyChecker) -> 'IHSLabelable':
        return QuickXPlainLabeler(checker, self.initial_parameters)
