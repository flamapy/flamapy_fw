"""Execution helpers: the OperationResult envelope and the async execution engine.

This is the seam where provenance is captured: callers that want the envelope (the CLI's
``-v`` flag, the benchmark harness, and — from 3.0 — the facade itself) run operations
through :func:`run_and_wrap` instead of calling ``execute``/``get_result`` directly.
``Operation.execute/get_result`` are untouched: plugin authors need no migration.

Since 2.9 the module also hosts the additive async API: :class:`ExecutionEngine` runs
operations on a thread pool (models are not picklable; the SAT/BDD/SMT solvers release
the GIL inside their C cores) and hands back :class:`Job` objects with timeout and
cancellation. Cancellation is **cooperative**: operations that implement the
:class:`Interruptible` protocol check the interrupt event inside their Python loops, but
a call that is deep inside solver C code cannot be interrupted — the job is abandoned
(its thread keeps running to completion) and only the result is discarded.
"""
import threading
import time
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from enum import Enum
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from flamapy.core.exceptions import OperationTimeout
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


@runtime_checkable
class Interruptible(Protocol):
    """Operations that can be cancelled cooperatively.

    The engine hands the operation an event before executing; long-running Python loops
    should check ``event.is_set()`` and stop early (returning a partial or empty result).
    """

    def set_interrupt_event(self, event: threading.Event) -> None:
        ...  # pylint: disable=unnecessary-ellipsis


class JobStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class Job:
    """A handle to an asynchronously executing operation."""

    def __init__(self, future: 'Future[OperationResult[Any]]',
                 interrupt_event: threading.Event,
                 result_adapter: Optional[Callable[[Any], Any]] = None) -> None:
        self._future = future
        self._interrupt_event = interrupt_event
        self._result_adapter = result_adapter

    @property
    def status(self) -> JobStatus:
        if self._future.cancelled() or self._interrupt_event.is_set():
            return JobStatus.CANCELLED
        if self._future.done():
            return JobStatus.FAILED if self._future.exception() else JobStatus.COMPLETED
        return JobStatus.RUNNING if self._future.running() else JobStatus.PENDING

    @property
    def cancelled(self) -> bool:
        return self.status is JobStatus.CANCELLED

    def cancel(self) -> None:
        """Request cancellation: cooperative for running jobs, immediate for queued ones."""
        self._interrupt_event.set()
        self._future.cancel()

    def envelope(self, timeout: Optional[float] = None) -> OperationResult[Any]:
        """The full OperationResult (blocking). See :meth:`result` for the value only."""
        try:
            return self._future.result(timeout)
        except FutureTimeoutError as error:
            self.cancel()
            raise OperationTimeout(
                f'Operation did not finish within {timeout} seconds '
                '(cancellation requested; a call inside solver C code cannot be '
                'interrupted and is abandoned).') from error

    def result(self, timeout: Optional[float] = None) -> Any:
        """The operation's value, waiting up to ``timeout`` seconds.

        Raises :class:`OperationTimeout` on expiry (after requesting cancellation) and
        re-raises any exception the operation itself raised.
        """
        value = self.envelope(timeout).value
        return self._result_adapter(value) if self._result_adapter is not None else value


class ExecutionEngine:
    """Runs operations asynchronously on bounded daemon worker threads.

    Daemon threads on purpose: a cancelled job whose operation is stuck inside solver C
    code is *abandoned* — it must never block interpreter exit (a plain
    ``ThreadPoolExecutor`` joins its workers at exit, which would hang the process on such
    a job forever). Abandoned jobs simply die with the process; their results are
    discarded.
    """

    def __init__(self, max_workers: Optional[int] = None) -> None:
        import os  # noqa: PLC0415
        self._slots = threading.BoundedSemaphore(max_workers or (os.cpu_count() or 4))

    # pylint: disable=too-many-arguments
    def submit(  # noqa: PLR0913 — keyword-only submission inputs are the documented API
        self,
        operation: Operation,
        model: Optional[VariabilityModel],
        *,
        operation_name: Optional[str] = None,
        plugin: Optional[str] = None,
        model_hash: Optional[str] = None,
        result_adapter: Optional[Callable[[Any], Any]] = None,
    ) -> Job:
        """Schedule ``operation`` on ``model``; returns immediately with a :class:`Job`."""
        interrupt_event = threading.Event()
        if isinstance(operation, Interruptible):
            operation.set_interrupt_event(interrupt_event)
        future: 'Future[OperationResult[Any]]' = Future()

        def runner() -> None:
            with self._slots:
                if not future.set_running_or_notify_cancel():
                    return  # cancelled while queued
                try:
                    future.set_result(run_and_wrap(
                        operation, model, operation_name=operation_name,
                        plugin=plugin, model_hash=model_hash))
                except BaseException as error:  # pylint: disable=broad-except
                    future.set_exception(error)

        threading.Thread(target=runner, daemon=True, name='flamapy-job').start()
        return Job(future, interrupt_event, result_adapter)

    def shutdown(self, wait: bool = True) -> None:  # pylint: disable=unused-argument
        """Kept for API symmetry: daemon workers need no explicit shutdown."""


_DEFAULT_ENGINE: Optional[ExecutionEngine] = None


def default_engine() -> ExecutionEngine:
    """The process-wide engine used by the facade's async API."""
    global _DEFAULT_ENGINE  # noqa: PLW0603  pylint: disable=global-statement
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = ExecutionEngine()
    return _DEFAULT_ENGINE
