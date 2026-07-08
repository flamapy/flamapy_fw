"""Solver-agnostic protocol for the reasoning algorithms.

QuickXPlain/FastDiag/HSDAG operate on integer constraint-index lists and only need a
consistency oracle; any solver backend can provide one by implementing this protocol
(the pysat_diagnosis plugin ships the glucose3 implementation).
"""
from typing import List, Protocol, runtime_checkable


@runtime_checkable
class ConsistencyChecker(Protocol):
    def is_consistent(self, set_c: List[int], delta: List[int]) -> bool:
        """Whether the knowledge base plus ``set_c`` (minus ``delta``) is satisfiable."""
        ...  # pylint: disable=unnecessary-ellipsis

    def delete(self) -> None:
        """Release solver resources."""
        ...  # pylint: disable=unnecessary-ellipsis
