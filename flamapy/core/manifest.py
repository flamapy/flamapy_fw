"""Plugin capability manifests.

A plugin describes what it can handle by declaring a module attribute ``MANIFEST`` (a
:class:`PluginManifest`) in its package ``__init__``. Discovery reads it via
:attr:`flamapy.core.plugins.Plugin.manifest`; plugins without one get a conservative
synthesized default (BOOLEAN level, exact, default cost), so third-party plugins keep
working unchanged.

Nothing routes on manifests yet — they are metadata for the 3.0 query planner, the docs
generator and the benchmark calibration. Costs are relative weights (lower is cheaper),
to be refined from benchmark data rather than guessed precisely.
"""
from dataclasses import dataclass, field
from typing import Optional

from flamapy.core.models.language_level import LanguageLevel, MajorLevel

DEFAULT_COST = 100


@dataclass(frozen=True)
class OperationCapability:
    """How a plugin implements one logical operation (keyed by its facade name)."""

    exact: bool = True                     # False => approximate/estimated results
    max_features: Optional[int] = None     # practical scale ceiling; None => unbounded
    cost: int = DEFAULT_COST               # relative cost weight (lower is cheaper)


@dataclass(frozen=True)
class PluginManifest:
    name: str
    extension: Optional[str] = None        # the plugin's model extension, if it has a model
    supported_level: LanguageLevel = field(
        default_factory=lambda: LanguageLevel(MajorLevel.BOOLEAN, set()))
    default_cost: int = DEFAULT_COST
    operations: dict[str, OperationCapability] = field(default_factory=dict)

    def supports(self, model_level: LanguageLevel) -> bool:
        """Whether a model at ``model_level`` is within this plugin's declared capability."""
        return (self.supported_level.major.value >= model_level.major.value
                and model_level.minors <= self.supported_level.minors)

    def capability(self, operation_name: str) -> OperationCapability:
        """The declared capability for an operation, or a default-cost exact one."""
        return self.operations.get(
            operation_name, OperationCapability(cost=self.default_cost))


def synthesized_manifest(name: str, extension: Optional[str] = None) -> PluginManifest:
    """The conservative default for plugins that declare no MANIFEST."""
    return PluginManifest(name=name, extension=extension)
