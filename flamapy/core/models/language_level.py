"""UVL language levels, as core vocabulary.

Historically these lived in ``flamapy.metamodels.fm_metamodel.operations.fm_language_level``;
they are dependency-free and now also describe plugin capability (see
:mod:`flamapy.core.manifest`), so they belong in the framework. The fm_metamodel re-exports
them from the old path for compatibility (shim removed in 3.1); ``calculate_language_level``
stays in fm_metamodel, where the feature-model knowledge lives.
"""
from enum import Enum, auto
from dataclasses import dataclass, field


class MajorLevel(Enum):
    BOOLEAN = 1
    ARITHMETIC = 2
    TYPE = 3


class MinorLevel(Enum):
    STRING_CONSTRAINTS = auto()
    FEATURE_CARDINALITY = auto()
    AGGREGATE_FUNCTION = auto()
    GROUP_CARDINALITY = auto()


ALL_MINOR_LEVELS = frozenset(MinorLevel)


@dataclass(order=True, frozen=True)
class LanguageLevel:
    major: MajorLevel
    minors: set[MinorLevel] = field(default_factory=set)

    def __str__(self) -> str:
        minors_str = ', '.join(ext.name for ext in sorted(self.minors, key=lambda x: x.name))
        return f'Major: {self.major.name}, Minor: {{{minors_str}}}'
