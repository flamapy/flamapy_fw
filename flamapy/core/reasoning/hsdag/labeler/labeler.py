"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/tree/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List

from ...protocols import ConsistencyChecker


class LabelerType(Enum):
    CONFLICT = 1
    DIAGNOSIS = 2


@dataclass
class AbstractHSParameters:
    set_c: List[int]
    set_d: List[int]


class IHSLabelable(ABC):
    """
    Interface for the HSDAG's labeler
    """

    @abstractmethod
    def get_type(self) -> LabelerType:
        pass

    @abstractmethod
    def get_initial_parameters(self) -> AbstractHSParameters:
        pass

    @abstractmethod
    def get_label(self, parameters: AbstractHSParameters) -> List[List[int]]:
        pass

    @abstractmethod
    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters,
                                     arc_label: int) -> AbstractHSParameters:
        pass

    @abstractmethod
    def get_instance(self, checker: ConsistencyChecker) -> 'IHSLabelable':
        pass
