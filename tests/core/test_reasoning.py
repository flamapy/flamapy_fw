"""The reasoning algorithms are solver-agnostic: a synthetic consistency oracle suffices.

Toy knowledge base over constraint indices 1..4: the set is inconsistent exactly when both
1 and 2 are active. Minimal conflict = {1, 2}; minimal diagnoses = {1} and {2}.
"""
import itertools
import random

import pytest

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


class ConflictsChecker:
    """Inconsistent iff the active constraints contain one of the given conflicts."""

    def __init__(self, conflicts):
        self.conflicts = [frozenset(conflict) for conflict in conflicts]

    def is_consistent(self, set_c, delta):
        active = {item for item in set_c if item not in delta}
        return not any(conflict <= active for conflict in self.conflicts)

    def delete(self):
        pass


def _minimal(family):
    family = {frozenset(item) for item in family}
    return {item for item in family if not any(other < item for other in family)}


def _brute_force(universe, conflicts):
    """(minimal diagnoses = minimal hitting sets of the conflicts, minimal conflicts)."""
    minimal_conflicts = _minimal(conflicts)
    hitting_sets = [subset for size in range(len(universe) + 1)
                    for subset in itertools.combinations(universe, size)
                    if all(set(subset) & conflict for conflict in minimal_conflicts)]
    return _minimal(hitting_sets), minimal_conflicts


def _hsdag(universe, conflicts, labeler):
    checker = ConflictsChecker(conflicts)
    if labeler == 'fastdiag':
        hsdag = HSDAG(FastDiagLabeler(checker, FastDiagParameters(list(universe), [], [])))
    else:
        hsdag = HSDAG(QuickXPlainLabeler(checker, QuickXPlainParameters(list(universe), [], [])))
    hsdag.construct()
    return ({frozenset(diag) for diag in hsdag.get_diagnoses()},
            {frozenset(conflict) for conflict in hsdag.get_conflicts()})


@pytest.mark.parametrize('labeler', ['fastdiag', 'quickxplain'])
def test_hsdag_prunes_supersets_of_found_path_labels(labeler):
    # Conflicts {2} and {1, 3}: diagnoses {2, 1} and {2, 3}; the path {2, 3} found after {2}
    # must be closed, not reported as another (non-minimal) conflict.
    assert _hsdag([1, 2, 3], [[2], [1, 3]], labeler) == _brute_force([1, 2, 3], [[2], [1, 3]])


@pytest.mark.parametrize('labeler', ['fastdiag', 'quickxplain'])
def test_hsdag_nodes_with_equal_sums_are_different_nodes(labeler):
    # Paths {1, 4} and {2, 3} have the same sum but are different sets of constraints.
    universe, conflicts = [1, 2, 3, 4], [[1, 2], [3, 4], [1, 3], [2, 4]]
    assert _hsdag(universe, conflicts, labeler) == _brute_force(universe, conflicts)


@pytest.mark.parametrize('labeler', ['fastdiag', 'quickxplain'])
def test_hsdag_is_complete_on_random_conflict_families(labeler):
    rng = random.Random(7)
    for _ in range(300):
        universe = list(range(1, rng.randint(3, 8) + 1))
        conflicts = [rng.sample(universe, rng.randint(1, min(3, len(universe))))
                     for _ in range(rng.randint(1, 4))]
        assert _hsdag(universe, conflicts, labeler) == _brute_force(universe, conflicts), \
            (universe, conflicts)
