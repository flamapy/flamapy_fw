"""Solver-agnostic diagnosis/explanation algorithms (moved from pysat_diagnosis in 2.9).

The algorithms take a :class:`ConsistencyChecker` protocol; solver plugins provide the
concrete checker. The old import paths under
``flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis`` remain as shims
until 3.0 (removed with the major).
"""
from .protocols import ConsistencyChecker
from .fastdiag import FastDiag
from .quickxplain import QuickXPlain

__all__ = ['ConsistencyChecker', 'FastDiag', 'QuickXPlain']
