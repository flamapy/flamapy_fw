"""Execution helpers that wrap operation results in the OperationResult envelope.

This is the seam where provenance is captured: callers that want the envelope (the CLI's
``-v`` flag, the benchmark harness, and — from 3.0 — the facade itself) run operations
through :func:`run_and_wrap` instead of calling ``execute``/``get_result`` directly.
``Operation.execute/get_result`` are untouched: plugin authors need no migration.
"""
import time
from typing import Any, Optional

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.result import OperationResult


def run_and_wrap(
    operation: Operation,
    model: Optional[VariabilityModel],
    *,
    operation_name: Optional[str] = None,
    plugin: Optional[str] = None,
    model_hash: Optional[str] = None,
) -> OperationResult[Any]:
    """Execute ``operation`` on ``model`` and wrap value + provenance in an envelope.

    ``model_hash`` may be passed pre-computed (the facade memoizes it per model);
    otherwise it is taken from ``model.canonical_hash()``. ``model`` is None for
    producer operations, which take no input model.
    """
    if model_hash is None and model is not None:
        model_hash = model.canonical_hash()
    start = time.perf_counter()
    operation.execute(model)  # type: ignore[arg-type]
    wall_time = time.perf_counter() - start
    return OperationResult(
        value=operation.get_result(),
        operation=operation_name or type(operation).__name__,
        plugin=plugin,
        backend=model.get_extension() if model is not None else None,
        exact=getattr(operation, 'exact', True),
        model_hash=model_hash,
        wall_time=wall_time,
    )
