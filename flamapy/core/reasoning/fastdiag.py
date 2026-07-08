"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/FastDiagV3.java
"""

import logging
from typing import List

from .protocols import ConsistencyChecker
from .utils import split, diff


class FastDiag:
    """
    Implementation of MSS-based FastDiag algorithm.
    Le, V. M., Silva, C. V., Felfernig, A., Benavides, D., Galindo, J., & Tran, T. N. T. (2023).
    FastDiagP: An Algorithm for Parallelized Direct Diagnosis.
    arXiv preprint arXiv:2305.06951.
    """

    def __init__(self, checker: ConsistencyChecker) -> None:
        self.checker = checker

    def find_diagnosis(self, set_c: List[int], set_b: List[int]) -> List[int]:
        """
        Activate FastDiag algorithm if there exists at least one constraint,
        which induces an inconsistency in B. Otherwise, it returns an empty set.

        // Func FastDiag(C, B) : Δ
        // if isEmpty(C) or consistent(B U C) return Φ
        // else return C \\ FD(Φ, C, B)
        :param set_c: a consideration set of constraints
        :param set_b: a background knowledge
        :return: a diagnosis or an empty set
        """
        logging.debug('fastDiag [C=%s, B=%s]', set_c, set_b)
        # print(f'fastDiag [C={C}, B={B}]')

        # if isEmpty(C) or consistent(B U C) return Φ
        if len(set_c) == 0 or self.checker.is_consistent(set_b + set_c, []):
            logging.debug('return Φ')
            # print('return Φ')
            return []

        # return C \ FD(C, B, Φ)
        mss = self._fd([], set_c, set_b)
        diag = diff(set_c, mss)

        logging.debug('return %s', diag)
        # print(f'return {diag}')
        return diag

    def _fd(self, delta: List[int], set_c: List[int], set_b: List[int]) -> List[int]:
        """
        The implementation of MSS-based FastDiag algorithm.
        The algorithm determines a maximal satisfiable subset MSS (Γ) of C U B.

        // Func FD(Δ, C = {c1..cn}, B) : MSS
        // if Δ != Φ and consistent(B U C) return C;
        // if singleton(C) return Φ;
        // k = n/2;
        // C1 = {c1..ck}; C2 = {ck+1..cn};
        // Δ1 = FD(C2, C1, B);
        // Δ2 = FD(C1 - Δ1, C2, B U Δ1);
        // return Δ1 ∪ Δ2;
        :param delta: check to skip redundant consistency checks
        :param set_c: a consideration set of constraints
        :param set_b: a background knowledge
        :return: a maximal satisfiable subset MSS of C U B
        """
        logging.debug('>>> FD [Δ=%s, C=%s, B=%s]', delta, set_c, set_b)

        # if Δ != Φ and consistent(B U C) return C;
        if len(delta) != 0 and self.checker.is_consistent(set_b + set_c, delta):
            logging.debug('<<< return %s', set_c)
            return set_c

        # if singleton(C) return Φ;
        if len(set_c) == 1:
            logging.debug('<<< return Φ')
            return []

        # C1 = {c1..ck}; C2 = {ck+1..cn};
        set_c1, set_c2 = split(set_c)

        # Δ1 = FD(C2, C1, B);
        delta1 = self._fd(set_c2, set_c1, set_b)
        # Δ2 = FD(C1 - Δ1, C2, B U Δ1);
        c1_without_delta1 = diff(set_c1, delta1)
        delta2 = self._fd(c1_without_delta1, set_c2, set_b + delta1)

        logging.debug('<<< return [Δ1={Δ1} ∪ Δ2={Δ2}]')

        # return Δ1 + Δ2
        return delta1 + delta2
