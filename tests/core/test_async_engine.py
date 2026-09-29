import threading
import time

import pytest

from flamapy.core.exceptions import OperationTimeout
from flamapy.core.execution import ExecutionEngine, Interruptible, JobStatus, run_and_wrap
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation


class FakeModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'fake'


class QuickOperation(Operation):
    def __init__(self, value=42):
        self.value = value
        self.result = None

    def execute(self, model):
        self.result = self.value
        return self

    def get_result(self):
        return self.result


class FailingOperation(QuickOperation):
    def execute(self, model):
        raise ValueError('boom')


class SlowInterruptibleOperation(Operation):
    """Counts until interrupted (or a generous ceiling): tests cooperative cancel."""

    def __init__(self):
        self.result = 0
        self._event = None
        self.started = threading.Event()

    def set_interrupt_event(self, event):
        self._event = event

    def execute(self, model):
        self.started.set()
        for _ in range(10_000):
            if self._event is not None and self._event.is_set():
                break
            self.result += 1
            time.sleep(0.001)
        return self

    def get_result(self):
        return self.result


@pytest.fixture(name='engine')
def _engine():
    engine = ExecutionEngine(max_workers=2)
    yield engine
    engine.shutdown(wait=False)


def test_job_completes_with_value_and_envelope(engine):
    job = engine.submit(QuickOperation(), FakeModel(), operation_name='quick')
    assert job.result(timeout=5) == 42
    assert job.status is JobStatus.COMPLETED
    envelope = job.envelope()
    assert envelope.operation == 'quick' and envelope.backend == 'fake'


def test_result_adapter_is_applied(engine):
    job = engine.submit(QuickOperation(), FakeModel(),
                        result_adapter=lambda value: value * 2)
    assert job.result(timeout=5) == 84


def test_operation_errors_are_raised_not_swallowed(engine):
    job = engine.submit(FailingOperation(), FakeModel())
    with pytest.raises(ValueError, match='boom'):
        job.result(timeout=5)
    assert job.status is JobStatus.FAILED


def test_timeout_raises_and_requests_cancel(engine):
    operation = SlowInterruptibleOperation()
    job = engine.submit(operation, FakeModel())
    with pytest.raises(OperationTimeout):
        job.result(timeout=0.05)
    assert job.cancelled


def test_cooperative_cancel_stops_an_interruptible_operation(engine):
    operation = SlowInterruptibleOperation()
    assert isinstance(operation, Interruptible)
    job = engine.submit(operation, FakeModel())
    operation.started.wait(timeout=5)
    job.cancel()
    # The loop notices the event and finishes early with a partial count.
    envelope = job.envelope(timeout=5)
    assert envelope.value < 10_000
    assert job.status is JobStatus.CANCELLED


def test_queued_job_can_be_cancelled_before_running():
    engine = ExecutionEngine(max_workers=1)
    try:
        blocker = SlowInterruptibleOperation()
        first = engine.submit(blocker, FakeModel())
        blocker.started.wait(timeout=5)
        queued = engine.submit(QuickOperation(), FakeModel())
        queued.cancel()
        assert queued.status is JobStatus.CANCELLED
        first.cancel()
    finally:
        engine.shutdown(wait=False)


def test_submit_call_runs_the_whole_task_inside_the_job(engine):
    # Preparation done by the task (e.g. a slow model transformation) happens on the
    # worker thread: submission returns at once and the deadline covers the task.
    def slow_task(interrupt_event):
        time.sleep(2)
        return run_and_wrap(QuickOperation(), FakeModel())

    start = time.perf_counter()
    job = engine.submit_call(slow_task)
    assert time.perf_counter() - start < 1
    with pytest.raises(OperationTimeout):
        job.result(timeout=0.2)


def test_submit_call_hands_the_interrupt_event_to_the_task(engine):
    received = []

    def task(interrupt_event):
        received.append(interrupt_event)
        return run_and_wrap(QuickOperation(7), FakeModel(), operation_name='quick')

    job = engine.submit_call(task, result_adapter=lambda value: value + 1)
    assert job.result(timeout=5) == 8
    assert isinstance(received[0], threading.Event) and not received[0].is_set()


def test_submit_call_propagates_task_errors(engine):
    def failing_task(interrupt_event):
        raise ValueError('preparation failed')

    job = engine.submit_call(failing_task)
    with pytest.raises(ValueError, match='preparation failed'):
        job.result(timeout=5)
    assert job.status is JobStatus.FAILED
