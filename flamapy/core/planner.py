"""The query planner: pick the best backend for an operation on a given model.

Opt-in in 2.8 (the facade engages it only under ``backend='auto'`` /
``FLAMAPY_BACKEND=auto``); in 3.0 it becomes the default router. Candidates are filtered by
the plugins' capability manifests (availability, language level, scale, exactness) and
ranked by their estimated cost: the cost of building the backend model (the plugin's
``transformation_cost`` for each step of the shortest model-to-model chain, waived for a model
the caller already holds or has cached as an artifact) plus the operation's cost at the model's
size. Plugins whose manifest declares no ``calibration`` are ranked after the calibrated ones.
The operation's historical ``default_backend`` gets a bonus so that, on plain Boolean
models, the planner reproduces today's routing where the estimates are close; 3.0 drops it.
"""
import warnings
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional

from flamapy.core.exceptions import NoCompatibleBackendError
from flamapy.core.manifest import OperationCapability, PluginManifest
from flamapy.core.models.language_level import LanguageLevel
from flamapy.core.plugins import Plugin, Plugins

# Scoring weights, in the manifests' unit (estimated milliseconds). A transformation step whose
# destination has no plugin manifest costs CHAIN_STEP_WEIGHT; matching the descriptor's
# historical default backend is worth DEFAULT_BACKEND_BONUS.
CHAIN_STEP_WEIGHT = 100
DEFAULT_BACKEND_BONUS = 150
# Deprecated since 2.9 and ignored: a cached artifact now waives the transformation cost
# instead of earning a bonus. Kept so 2.8 code that imports it or passes it keeps working;
# removed in 3.0.
ARTIFACT_BONUS = 100

# Descriptor default_backend values are facade backend names; 'sat' is the one name that
# differs from its model extension.
DEFAULT_BACKEND_EXTENSIONS = {'sat': 'pysat'}


@dataclass(frozen=True)
class PlannerPolicy:
    chain_step_weight: int = CHAIN_STEP_WEIGHT
    default_backend_bonus: int = DEFAULT_BACKEND_BONUS
    artifact_bonus: int = ARTIFACT_BONUS  # deprecated and ignored, see ARTIFACT_BONUS

    def __post_init__(self) -> None:
        if self.artifact_bonus != ARTIFACT_BONUS:
            warnings.warn(
                'PlannerPolicy.artifact_bonus is ignored since flamapy 2.9 (a cached artifact '
                'waives the transformation cost) and will be removed in 3.0.',
                DeprecationWarning, stacklevel=3)


DEFAULT_POLICY = PlannerPolicy()


@dataclass(frozen=True)
class Plan:
    plugin_name: str
    target_extension: str
    transformation_chain: tuple[tuple[str, str], ...]  # (source_ext, destination_ext) steps
    rationale: str
    score: int = 0
    alternatives: tuple[str, ...] = field(default=())
    # Added in 2.9, last so that 2.8 positional construction keeps working: the transformation
    # + operation estimate in ms, before the bonus. A heuristic from the calibration machine,
    # useful to compare candidates, not a prediction of the wall time on yours.
    estimated_cost: int = 0

    def to_dict(self, source_extension: str = 'fm') -> dict[str, Any]:
        """The plan as plain data, in the vocabulary of the result envelope (used by the CLI
        and the REST API)."""
        return {
            'plugin': self.plugin_name,
            'backend': self.target_extension,
            'transformation_chain': [source_extension,
                                     *(dst for _, dst in self.transformation_chain)],
            'estimated_cost_ms': self.estimated_cost,
            'rationale': self.rationale,
            'alternatives': list(self.alternatives),
        }


def _shortest_chains(
    source_extension: str, m2m_edges: Iterable[tuple[str, str]]
) -> dict[str, tuple[tuple[str, str], ...]]:
    """BFS over the m2m extension graph: extension -> shortest chain from the source."""
    adjacency: dict[str, list[str]] = {}
    for src, dst in m2m_edges:
        adjacency.setdefault(src, []).append(dst)
    chains: dict[str, tuple[tuple[str, str], ...]] = {source_extension: ()}
    queue = deque([source_extension])
    while queue:
        current = queue.popleft()
        for nxt in sorted(adjacency.get(current, [])):
            if nxt in chains:
                continue
            chains[nxt] = chains[current] + ((current, nxt),)
            queue.append(nxt)
    return chains


def _implements(plugin: Plugin, operation_name: str) -> bool:
    for operation in plugin.operations:
        descriptor = getattr(operation, 'facade', None)
        if descriptor is not None and descriptor.name == operation_name:
            return True
    return False


def _descriptor_default_backend(plugins: Plugins, operation_name: str) -> Optional[str]:
    for plugin in plugins:
        for operation in plugin.operations:
            descriptor = getattr(operation, 'facade', None)
            if descriptor is not None and descriptor.name == operation_name:
                default = descriptor.default_backend
                name = default.value if hasattr(default, 'value') else default
                return DEFAULT_BACKEND_EXTENSIONS.get(name, name)
    return None


def _plugin_extension(plugin: Plugin, source_extension: str) -> str:
    return plugin.manifest.extension or source_extension


@dataclass(frozen=True)
class _Route:
    """The cost of reaching a backend model along a transformation chain."""

    cost: int
    reasons: tuple[str, ...]


def _route(  # noqa: PLR0913 — one keyword per input of the estimate
    chain: tuple[tuple[str, str], ...],
    *,
    n_features: int,
    by_extension: dict[str, Plugin],
    available_models: frozenset[str],
    artifact_available: Callable[[str], bool],
    policy: PlannerPolicy,
) -> _Route:
    cost = 0
    reasons: list[str] = []
    for _, destination in chain:
        if destination in available_models:
            reasons.append(f'{destination} model already built')
            continue
        if artifact_available(destination):
            reasons.append(f'cached artifact for {destination}')
            continue
        plugin = by_extension.get(destination)
        cost += (plugin.manifest.transformation_cost_at(n_features) if plugin is not None
                 else policy.chain_step_weight)
    return _Route(cost, tuple(reasons))


def _rejection(  # noqa: PLR0913 — one check per manifest field
    manifest: PluginManifest,
    *,
    capability: OperationCapability,
    extension: str,
    chains: dict[str, tuple[tuple[str, str], ...]],
    model_level: LanguageLevel,
    n_features: int,
    allow_approximate: bool,
) -> Optional[str]:
    """Why a plugin cannot run the operation on this model, or None when it can."""
    if not manifest.available:
        return manifest.unavailable_reason or 'unavailable'
    if extension not in chains:
        return f'no transformation path to {extension!r}'
    if not manifest.supports(model_level):
        return f'supports {manifest.supported_level}, model is {model_level}'
    if capability.max_features is not None and n_features > capability.max_features:
        return f'model has {n_features} features, declared limit is {capability.max_features}'
    if not capability.exact and not allow_approximate:
        return 'approximate (pass allow_approximate=True)'
    return None


# pylint: disable=too-many-locals
def plan(  # noqa: PLR0913 — keyword-only planning inputs are the documented API
    operation_name: str,
    *,
    source_extension: str,
    model_level: LanguageLevel,
    n_features: int,
    plugins: Plugins,
    m2m_edges: Iterable[tuple[str, str]],
    artifact_available: Callable[[str], bool] = lambda extension: False,
    available_models: Iterable[str] = (),
    allow_approximate: bool = False,
    policy: PlannerPolicy = DEFAULT_POLICY,
) -> Plan:
    """Choose the plugin/backend to run ``operation_name`` on a model.

    ``m2m_edges`` are the available model-to-model transformations as
    ``(source_extension, destination_extension)`` pairs; ``source_extension`` is the model's
    own extension (normally ``fm``). ``available_models`` are the extensions of the backend
    models the caller already holds (their transformation costs nothing more), and
    ``artifact_available`` tells which ones are cached on disk. Approximate implementations
    (``exact=False`` in the manifest) are only candidates with ``allow_approximate``.

    Raises :class:`NoCompatibleBackendError` when no installed plugin both implements the
    operation and supports the model's language level / scale.
    """
    chains = _shortest_chains(source_extension, m2m_edges)
    default_backend = _descriptor_default_backend(plugins, operation_name)
    by_extension = {_plugin_extension(plugin, source_extension): plugin for plugin in plugins}
    built = frozenset(available_models)

    scored: list[tuple[bool, int, str, Plan]] = []
    rejected: list[str] = []
    for plugin in plugins:
        if not _implements(plugin, operation_name):
            continue
        manifest = plugin.manifest
        extension = _plugin_extension(plugin, source_extension)
        capability = manifest.capability(operation_name)
        reason = _rejection(manifest, capability=capability, extension=extension, chains=chains,
                            model_level=model_level, n_features=n_features,
                            allow_approximate=allow_approximate)
        if reason is not None:
            rejected.append(f'{manifest.name}: {reason}')
            continue

        chain = chains[extension]
        route = _route(chain, n_features=n_features, by_extension=by_extension,
                       available_models=built, artifact_available=artifact_available,
                       policy=policy)
        operation_cost = capability.cost_at(n_features)
        estimate = route.cost + operation_cost
        score = estimate
        reasons = [f'estimated {estimate} ms (transformation {route.cost}, '
                   f'operation {operation_cost})', *route.reasons]
        if default_backend is not None and extension == default_backend:
            score -= policy.default_backend_bonus
            reasons.append('historical default backend')
        if not capability.exact:
            reasons.append('approximate')
        uncalibrated = manifest.calibration is None
        if uncalibrated:
            reasons.append('uncalibrated estimate, ranked after calibrated plugins')
        scored.append((uncalibrated, score, manifest.name, Plan(
            plugin_name=plugin.name,
            target_extension=extension,
            transformation_chain=chain,
            rationale=f'{manifest.name}: ' + ', '.join(reasons),
            score=score,
            estimated_cost=estimate,
        )))

    if not scored:
        details = '; '.join(rejected) if rejected else 'no plugin implements it'
        raise NoCompatibleBackendError(
            f"No installed backend can run '{operation_name}' on this model "
            f'({model_level}, {n_features} features): {details}')

    # Calibrated estimates first, then by score, then by name (deterministic).
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    best = scored[0][3]
    alternatives = tuple(entry[3].plugin_name for entry in scored[1:])
    return Plan(
        plugin_name=best.plugin_name,
        target_extension=best.target_extension,
        transformation_chain=best.transformation_chain,
        rationale=best.rationale,
        score=best.score,
        estimated_cost=best.estimated_cost,
        alternatives=alternatives,
    )
