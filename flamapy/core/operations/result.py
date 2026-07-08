"""The typed result envelope: an operation's value plus its provenance.

In 2.7 this is opt-in machinery — the facade and CLI still return bare values by default
(the CLI's ``-v`` flag prints the provenance, and consumers like the benchmark harness use
:func:`flamapy.core.execution.run_and_wrap` directly). In 3.0 the envelope becomes the
facade/CLI return type.
"""
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar('T')


@dataclass(frozen=True)
class OperationResult(Generic[T]):
    value: T
    operation: str                       # logical operation name (facade/descriptor name)
    plugin: Optional[str] = None         # plugin that executed it
    backend: Optional[str] = None        # model extension it ran on
    exact: bool = True                   # False for approximate/estimated results
    model_hash: Optional[str] = None     # canonical content hash of the analyzed model
    wall_time: float = 0.0               # seconds spent in execute()
    planner: Optional[str] = None        # how the backend was chosen (3.0 planner)
    cache_hit: bool = False              # artifact cache hit (3.0 cache)
    metadata: dict[str, Any] = field(default_factory=dict)

    def unwrap(self) -> T:
        return self.value

    def to_dict(self) -> dict[str, Any]:
        return {
            'value': self.value,
            'operation': self.operation,
            'plugin': self.plugin,
            'backend': self.backend,
            'exact': self.exact,
            'model_hash': self.model_hash,
            'wall_time': self.wall_time,
            'planner': self.planner,
            'cache_hit': self.cache_hit,
            'metadata': self.metadata,
        }
