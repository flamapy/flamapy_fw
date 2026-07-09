import threading
import time

import pytest

from flamapy.core.exceptions import OperationTimeout
from flamapy.core.execution import ExecutionEngine, Interruptible, JobStatus
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
