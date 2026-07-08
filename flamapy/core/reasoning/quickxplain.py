"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/QuickXPlain.java
"""

import logging
from typing import List

from .protocols import ConsistencyChecker
from .utils import split


class QuickXPlain:
    """
    Implementation of QuickXPlain algorithm
    Junker, Ulrich. "Quickxplain: Conflict detection
    for arbitrary constraint propagation algorithms."
    IJCAI’01 Workshop on Modelling and Solving problems with constraints. Vol. 4. 2001.
    """

    def __init__(self, checker: ConsistencyChecker) -> None:
        self.checker = checker

    def find_conflict(self, set_c: List[int], set_b: List[int]) -> List[int]:
        """
        // Func QuickXPlain(C={c1,c2,…, cm}, B): CS
        // IF consistent(B∪C) return "No conflict";
        // IF isEmpty(C) return Φ;
        // ELSE return QX(Φ, C, B);
        :param set_c: a consideration set
        :param set_b: a background knowledge
        :return: a conflict set or an empty set
        """
        logging.debug('>>> QuickXPlain [C=%s, B=%s]', set_c, set_b)
        # print(f'quickXPlain [C={C}, B={B}]')

        # if C is empty or consistent(B U C) then return empty set
        if len(set_c) == 0 or self.checker.is_consistent(set_b + set_c, []):
            logging.debug('return Φ')
            # print('return Φ')
            return []

        # return QX(Φ, C, B)
        set_cs = self._qx([], set_c, set_b)

        logging.debug('return %s', set_cs)
        # print(f'return {cs}')
        return set_cs

    def _qx(self, set_d: List[int], set_c: List[int], set_b: List[int]) -> List[int]:
        """
        // func QX(Δ, C={c1,c2, …, cq}, B): CS
        // IF (Δ != Φ AND inconsistent(B)) return Φ;
        // IF singleton(C) return C;
        // k = q/2;
        // C1 <-- {c1, …, ck}; C2 <-- {ck+1, …, cq};
        // CS1 <-- QX(C2, C1, B ∪ C2);
        // CS2 <-- QX(CS1, C2, B ∪ CS1);
        // return (CS1 ∪ CS2)
        :param set_d: check to skip redundant consistency checks
        :param set_c: a consideration set of constraints
        :param set_b: a background knowledge
        :return: a conflict set or an empty set
        """
        logging.debug('>>> QX [D=%s, C=%s, B=%s]', set_d, set_c, set_b)

        # if D != Φ and inconsistent(B) then return Φ
        if len(set_d) != 0 and not self.checker.is_consistent(set_b, set_c):
            logging.debug('<<< return Φ')
            return []

        # if C is singleton then return C
        if len(set_c) == 1:
            logging.debug('<<< return %s', set_c)
            return set_c

        # C1 = {c1..ck}; C2 = {ck+1..cn};
        set_c1, set_c2 = split(set_c)

        # CS1 = QX(C2, C1, B U C2)
        cs1 = self._qx(set_c2, set_c1, (set_b + set_c2))
        # CS2 = QX(CS1, C2, B U CS1)
        cs2 = self._qx(cs1, set_c2, (set_b + cs1))

        logging.debug('<<< return %s', (cs1 + cs2))

        # return CS1 U CS2
        return cs1 + cs2
