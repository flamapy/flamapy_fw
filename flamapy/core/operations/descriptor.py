"""Self-describing metadata for operations, so the facade/CLI/REST can be *derived* from the
installed operations instead of hand-written.

An operation interface (or a bespoke concrete operation) declares a class attribute ``facade`` of
type :class:`OperationDescriptor`. It states the operation's stable public name, which backend it
runs on, its inputs (and how to wire them), and optional input/result adapters for the few
operations whose facade method is not a plain ``set params -> execute``. Concrete backend
implementations inherit the descriptor from their interface, so there is exactly one descriptor
per *logical* operation.
"""
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional


@dataclass(frozen=True)
class Input:
    """One input of a facade operation and how to feed it to the underlying operation."""

    name: str
    type: Any = str                   # a type or typing special form (e.g. Any), for CLI/REST
    default: Any = None
    required: bool = False
    setter: Optional[str] = None      # operation setter for the value, e.g. 'set_sample_size'
    kind: str = 'scalar'              # 'scalar' | 'configuration' | 'file' (CLI/REST marshalling)


@dataclass(frozen=True)
class OperationDescriptor:
    """Everything the facade/CLI/REST need to expose an operation without hand-written code."""

    name: str                                     # stable public (facade/CLI/REST) name
    operation: str                                # name passed to DiscoverMetamodels.use_operation
    kind: str = 'operation'                       # 'operation' | 'producer' | 'transformer'
    default_backend: Optional[str] = None         # None => runs directly on the feature model
    backends: Optional[tuple[str, ...]] = None    # allowed backends (None => any implementer)
    selectable_backend: bool = False              # facade exposes a backend= kwarg (else fixed)
    inputs: tuple[Input, ...] = ()
    # For the ~12 non-uniform methods: custom wiring / result reshaping. When absent, the generic
    # "call each Input.setter, then execute, then get_result" path is used.
    input_adapter: Optional[Callable[..., Any]] = None
    result_adapter: Optional[Callable[[Any], Any]] = None
    doc: str = ''
    returns: str = 'Any'                          # return annotation (source text) for the stub

    @property
    def needs_backend(self) -> bool:
        return self.default_backend is not None


def collect_descriptors(operations: Iterable[type]) -> dict[str, OperationDescriptor]:
    """Collect the ``facade`` descriptors from a set of operation classes, keyed by public name.

    Concrete backend operations inherit their interface's descriptor, so several classes may yield
    the same descriptor; they are de-duplicated by ``descriptor.name`` (first one wins).
    """
    descriptors: dict[str, OperationDescriptor] = {}
    for operation in operations:
        descriptor = getattr(operation, 'facade', None)
        if isinstance(descriptor, OperationDescriptor):
            descriptors.setdefault(descriptor.name, descriptor)
    return descriptors
