"""The reasoning algorithms are solver-agnostic: a synthetic consistency oracle suffices.

Toy knowledge base over constraint indices 1..4: the set is inconsistent exactly when both
1 and 2 are active. Minimal conflict = {1, 2}; minimal diagnoses = {1} and {2}.
"""
from flamapy.core.reasoning import ConsistencyChecker, FastDiag, QuickXPlain
from flamapy.core.reasoning.hsdag import HSDAG
from flamapy.core.reasoning.hsdag.labeler.fastdiag_labeler import (
    FastDiagLabeler,
    FastDiagParameters,
)
from flamapy.core.reasoning.hsdag.labeler.quickxplain_labeler import (
    QuickXPlainLabeler,
    QuickXPlainParameters,
)


class ToyChecker:
    """Inconsistent iff constraints 1 and 2 are both active (no solver involved)."""

    def is_consistent(self, set_c, delta):
        active = {item for item in set_c if item not in delta}
        return not {1, 2} <= active

    def delete(self):
        pass


def test_toy_checker_satisfies_the_protocol():
    assert isinstance(ToyChecker(), ConsistencyChecker)


def test_quickxplain_finds_the_minimal_conflict():
    conflict = QuickXPlain(ToyChecker()).find_conflict([1, 2, 3, 4], [])
    assert set(conflict) == {1, 2}


def test_quickxplain_returns_empty_when_consistent():
    assert QuickXPlain(ToyChecker()).find_conflict([1, 3, 4], []) == []


def test_fastdiag_finds_a_minimal_diagnosis():
    diagnosis = FastDiag(ToyChecker()).find_diagnosis([1, 2, 3, 4], [])
    assert diagnosis in ([1], [2])


def test_hsdag_enumerates_all_diagnoses_and_conflicts():
    parameters = FastDiagParameters([1, 2, 3, 4], [], [])
    hsdag = HSDAG(FastDiagLabeler(ToyChecker(), parameters))
    hsdag.construct()
    assert {frozenset(diag) for diag in hsdag.get_diagnoses()} == {frozenset({1}),
                                                                   frozenset({2})}

    parameters = QuickXPlainParameters([1, 2, 3, 4], [], [])
    hsdag = HSDAG(QuickXPlainLabeler(ToyChecker(), parameters))
    hsdag.construct()
    assert {frozenset(conflict) for conflict in hsdag.get_conflicts()} == {frozenset({1, 2})}


def test_max_number_diagnoses_limit():
    parameters = FastDiagParameters([1, 2, 3, 4], [], [])
    hsdag = HSDAG(FastDiagLabeler(ToyChecker(), parameters))
    hsdag.max_number_diagnoses = 1
    hsdag.construct()
    assert len(hsdag.get_diagnoses()) == 1
