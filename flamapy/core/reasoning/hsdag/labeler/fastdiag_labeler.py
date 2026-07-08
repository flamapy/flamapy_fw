"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/labeler/FastDiagV3Labeler.java
"""

from dataclasses import dataclass
from typing import List

from .labeler import IHSLabelable, LabelerType, AbstractHSParameters
from ...protocols import ConsistencyChecker
from ...fastdiag import FastDiag


@dataclass
class FastDiagParameters(AbstractHSParameters):
    set_b: List[int]

    def __str__(self) -> str:
        return f"FastDiagParameters{{C={self.set_c}, B={self.set_b}}}"


class FastDiagLabeler(FastDiag, IHSLabelable):
    """
    HSLabeler for FastDiag algorithm
    """

    def __init__(self, checker: ConsistencyChecker, parameters: FastDiagParameters):
        super().__init__(checker)
        self.initial_parameters = parameters

    def get_type(self) -> LabelerType:
        return LabelerType.DIAGNOSIS

    def get_initial_parameters(self) -> AbstractHSParameters:
        return self.initial_parameters

    def get_label(self, parameters: AbstractHSParameters) -> List[List[int]]:
        """
        Identifies a diagnosis
        """
        assert isinstance(parameters, FastDiagParameters), \
            "parameter must be an instance of FastDiagParameters"
        neg_c = [-1 * item for item in parameters.set_c]
        if len(parameters.set_c) >= 1 \
                and (len(parameters.set_b) == 0
                     or self.checker.is_consistent(parameters.set_b + neg_c, [])):

            diag = self.find_diagnosis(parameters.set_c, parameters.set_b)
            if len(diag) != 0:
                return [diag]
        return []

    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters,
                                     arc_label: int) -> AbstractHSParameters:
        """
        Identifies the new node's parameters on the basis of the parent node's parameters.
        """
        assert isinstance(param_parent_node, FastDiagParameters),\
            "parameter must be an instance of FastDiagParameters"

        new_c = param_parent_node.set_c.copy()
        new_c.remove(arc_label)
        new_b = param_parent_node.set_b.copy()
        new_b.append(arc_label)
        # D = param_parent_node.D.copy()
        # D.append(arcLabel)

        return FastDiagParameters(new_c, [], new_b)

    def get_instance(self, checker: ConsistencyChecker) -> IHSLabelable:
        return FastDiagLabeler(checker, self.initial_parameters)
