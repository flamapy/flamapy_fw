"""The query planner: pick the best backend for an operation on a given model.

Opt-in in 2.8 (the facade engages it only under ``backend='auto'`` /
``FLAMAPY_BACKEND=auto``); in 3.0 it becomes the default router. Candidates are filtered by
the plugins' capability manifests (language level + scale), routed over the shortest
model-to-model transformation chain, and ranked by declared cost — with a bonus for the
operation's historical ``default_backend`` so that, on plain Boolean models, the planner
reproduces today's routing exactly.
"""
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from flamapy.core.exceptions import NoCompatibleBackendError
from flamapy.core.models.language_level import LanguageLevel
from flamapy.core.plugins import Plugin, Plugins

# Scoring weights: one transformation step costs as much as a default-cost operation;
# matching the descriptor's historical default backend outweighs one step, and having a
# cached artifact for the target extension offsets the chain entirely.
CHAIN_STEP_WEIGHT = 100
DEFAULT_BACKEND_BONUS = 150
ARTIFACT_BONUS = 100

# Descriptor default_backend values are facade backend names; 'sat' is the one name that
# differs from its model extension.
DEFAULT_BACKEND_EXTENSIONS = {'sat': 'pysat'}


@dataclass(frozen=True)
class PlannerPolicy:
    chain_step_weight: int = CHAIN_STEP_WEIGHT
    default_backend_bonus: int = DEFAULT_BACKEND_BONUS
    artifact_bonus: int = ARTIFACT_BONUS


DEFAULT_POLICY = PlannerPolicy()


@dataclass(frozen=True)
class Plan:
    plugin_name: str
    target_extension: str
    transformation_chain: tuple[tuple[str, str], ...]  # (source_ext, destination_ext) steps
    rationale: str
    score: int = 0
    alternatives: tuple[str, ...] = field(default=())


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
    return any(
        getattr(operation, 'facade', None) is not None
        and operation.facade.name == operation_name
        for operation in plugin.operations)


def _descriptor_default_backend(plugins: Plugins, operation_name: str) -> Optional[str]:
    for plugin in plugins:
        for operation in plugin.operations:
            descriptor = getattr(operation, 'facade', None)
            if descriptor is not None and descriptor.name == operation_name:
                default = descriptor.default_backend
                name = default.value if hasattr(default, 'value') else default
                return DEFAULT_BACKEND_EXTENSIONS.get(name, name)
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
    policy: PlannerPolicy = DEFAULT_POLICY,
) -> Plan:
    """Choose the plugin/backend to run ``operation_name`` on a model.

    ``m2m_edges`` are the available model-to-model transformations as
    ``(source_extension, destination_extension)`` pairs;
    ``source_extension`` is the model's own extension (normally ``fm``).

    Raises :class:`NoCompatibleBackendError` when no installed plugin both implements the
    operation and supports the model's language level / scale.
    """
    chains = _shortest_chains(source_extension, m2m_edges)
    default_backend = _descriptor_default_backend(plugins, operation_name)

    scored: list[tuple[int, str, Plan]] = []
    rejected: list[str] = []
    for plugin in plugins:
        if not _implements(plugin, operation_name):
            continue
        manifest = plugin.manifest
        extension = manifest.extension or source_extension
        if extension not in chains:
            rejected.append(f'{manifest.name}: no transformation path to {extension!r}')
            continue
        if not manifest.supports(model_level):
            rejected.append(
                f'{manifest.name}: supports {manifest.supported_level}, '
                f'model is {model_level}')
            continue
        capability = manifest.capability(operation_name)
        if capability.max_features is not None and n_features > capability.max_features:
            rejected.append(
                f'{manifest.name}: model has {n_features} features, '
                f'declared limit is {capability.max_features}')
            continue

        chain = chains[extension]
        score = len(chain) * policy.chain_step_weight + capability.cost
        reasons = [f'cost {capability.cost}', f'{len(chain)} transformation step(s)']
        if default_backend is not None and extension == default_backend:
            score -= policy.default_backend_bonus
            reasons.append('historical default backend')
        if artifact_available(extension):
            score -= policy.artifact_bonus
            reasons.append('cached artifact available')
        if not capability.exact:
            reasons.append('approximate')
        scored.append((score, manifest.name, Plan(
            plugin_name=plugin.name,
            target_extension=extension,
            transformation_chain=chain,
            rationale=f'{manifest.name}: ' + ', '.join(reasons),
            score=score,
        )))

    if not scored:
        details = '; '.join(rejected) if rejected else 'no plugin implements it'
        raise NoCompatibleBackendError(
            f"No installed backend can run '{operation_name}' on this model "
            f'({model_level}, {n_features} features): {details}')

    scored.sort(key=lambda item: (item[0], item[1]))  # deterministic: score, then name
    best = scored[0][2]
    alternatives = tuple(entry[2].plugin_name for entry in scored[1:])
    return Plan(
        plugin_name=best.plugin_name,
        target_extension=best.target_extension,
        transformation_chain=best.transformation_chain,
        rationale=best.rationale,
        score=best.score,
        alternatives=alternatives,
    )
