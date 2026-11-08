"""Plugin capability manifests.

A plugin describes what it can handle by declaring a module attribute ``MANIFEST`` (a
:class:`PluginManifest`) in its package ``__init__``. Discovery reads it via
:attr:`flamapy.core.plugins.Plugin.manifest`; plugins without one get a conservative
synthesized default (BOOLEAN level, exact, default cost), so third-party plugins keep
working unchanged.

The query planner (:mod:`flamapy.core.planner`) routes on manifests when the caller asks for
``backend='auto'``; the docs generator and the benchmark calibration read them too.

Costs are estimated milliseconds: the time the operation (or, for ``transformation_cost``,
building the plugin's model from the feature model) takes on a model of a given size, measured
on the calibration models (see each plugin's ``__init__``). They only have to be right relative
to each other: the planner adds the transformation and the operation estimates of each candidate
and takes the smallest. A constant ``cost`` describes an operation whose time barely depends on
the model; a ``cost_curve`` gives the estimate per size bin for the ones that do.

A manifest names the run its costs come from in ``calibration``; the planner ranks manifests
without one (including the synthesized default) after every calibrated candidate, so an
unmeasured number never looks cheaper than a measured one. ``exact=False`` capabilities are
only chosen with ``allow_approximate``.
"""
from dataclasses import dataclass, field, replace
from typing import Optional

from flamapy.core.models.language_level import LanguageLevel, MajorLevel

DEFAULT_COST = 100
DEFAULT_TRANSFORMATION_COST = 100

# ((features, cost), ...) in increasing order of features: the cost applies to models with at
# most that many features. Beyond the last entry the cost grows in proportion to the size, so a
# curve measured on small models never makes a larger one look as cheap (the plugin's
# max_features is the place to stop them altogether).
CostCurve = tuple[tuple[int, int], ...]


def cost_at(curve: CostCurve, n_features: int, default: int) -> int:
    """The cost of a curve for a model of ``n_features`` features (``default`` when it is empty)."""
    if not curve:
        return default
    for bound, cost in curve:
        if n_features <= bound:
            return cost
    last_bound, last_cost = curve[-1]
    return -(-last_cost * n_features // max(last_bound, 1))  # ceiling of the linear growth


@dataclass(frozen=True)
class OperationCapability:
    """How a plugin implements one logical operation (keyed by its facade name)."""

    exact: bool = True                     # False => approximate/estimated results
    max_features: Optional[int] = None     # practical scale ceiling; None => unbounded
    cost: int = DEFAULT_COST               # estimated ms when no curve is declared
    cost_curve: CostCurve = ()             # estimated ms per size bin, see the module docstring

    def cost_at(self, n_features: int) -> int:
        """The estimated cost of the operation on a model of ``n_features`` features."""
        return cost_at(self.cost_curve, n_features, self.cost)


@dataclass(frozen=True)
class PluginManifest:
    name: str
    extension: Optional[str] = None        # the plugin's model extension, if it has a model
    supported_level: LanguageLevel = field(
        default_factory=lambda: LanguageLevel(MajorLevel.BOOLEAN, set()))
    default_cost: int = DEFAULT_COST
    # Plugin-wide scale ceiling, applied to every operation that declares none: the right
    # place for a limit that comes from building the model (e.g. BDD compilation).
    max_features: Optional[int] = None
    # Estimated ms to build this plugin's model from the feature model (constant or per size
    # bin); the planner charges it once per plan unless the model is already built or cached.
    transformation_cost: int = DEFAULT_TRANSFORMATION_COST
    transformation_cost_curve: CostCurve = ()
    # A plugin whose runtime dependency is missing (an external binary, a native package)
    # declares itself unavailable with the reason; the planner reports it instead of choosing
    # a backend that would fail.
    available: bool = True
    unavailable_reason: str = ''
    # The calibration run the costs come from (e.g. '2026-11-06'); None for estimates that were
    # never measured, which the planner ranks after calibrated ones.
    calibration: Optional[str] = None
    operations: dict[str, OperationCapability] = field(default_factory=dict)

    def supports(self, model_level: LanguageLevel) -> bool:
        """Whether a model at ``model_level`` is within this plugin's declared capability."""
        return (self.supported_level.major.value >= model_level.major.value
                and model_level.minors <= self.supported_level.minors)

    def capability(self, operation_name: str) -> OperationCapability:
        """The declared capability for an operation, or a default-cost exact one; the
        plugin-wide ``max_features`` applies when the operation declares none."""
        declared = self.operations.get(operation_name)
        if declared is None:
            return OperationCapability(cost=self.default_cost, max_features=self.max_features)
        if declared.max_features is None and self.max_features is not None:
            return replace(declared, max_features=self.max_features)
        return declared

    def transformation_cost_at(self, n_features: int) -> int:
        """The estimated cost of building this plugin's model for ``n_features`` features."""
        return cost_at(self.transformation_cost_curve, n_features, self.transformation_cost)


def synthesized_manifest(name: str, extension: Optional[str] = None) -> PluginManifest:
    """The conservative default for plugins that declare no MANIFEST."""
    return PluginManifest(name=name, extension=extension)
