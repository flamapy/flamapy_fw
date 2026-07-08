from flamapy.core.execution import run_and_wrap
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation, OperationResult


class FakeModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'fake'

    def canonical_hash(self):
        return 'deadbeef'


class FakeOperation(Operation):
    def __init__(self) -> None:
        self.result = None

    def execute(self, model):
        self.result = 42
        return self

    def get_result(self):
        return self.result


class FakeApproximateOperation(FakeOperation):
    exact = False


class TestOperationResult:
    def test_unwrap_and_to_dict(self):
        result = OperationResult(value=[1, 2], operation='op', plugin='p', backend='b')
        assert result.unwrap() == [1, 2]
        as_dict = result.to_dict()
        assert as_dict['value'] == [1, 2]
        assert as_dict['operation'] == 'op'
        assert as_dict['exact'] is True
        assert as_dict['cache_hit'] is False
        assert as_dict['planner'] is None


class TestRunAndWrap:
    def test_wraps_value_and_provenance(self):
        envelope = run_and_wrap(
            FakeOperation(), FakeModel(), operation_name='fake_op', plugin='fake_plugin')
        assert envelope.value == 42
        assert envelope.operation == 'fake_op'
        assert envelope.plugin == 'fake_plugin'
        assert envelope.backend == 'fake'
        assert envelope.exact is True
        assert envelope.model_hash == 'deadbeef'
        assert envelope.wall_time >= 0.0

    def test_operation_name_defaults_to_class_name(self):
        assert run_and_wrap(FakeOperation(), FakeModel()).operation == 'FakeOperation'

    def test_exact_flag_is_reported(self):
        assert run_and_wrap(FakeApproximateOperation(), FakeModel()).exact is False

    def test_explicit_model_hash_wins(self):
        envelope = run_and_wrap(FakeOperation(), FakeModel(), model_hash='cafe')
        assert envelope.model_hash == 'cafe'

    def test_producer_without_model(self):
        envelope = run_and_wrap(FakeOperation(), None)
        assert envelope.backend is None and envelope.model_hash is None
        assert envelope.value == 42

    def test_default_canonical_hash_is_none(self):
        class HashlessModel(VariabilityModel):
            @staticmethod
            def get_extension() -> str:
                return 'x'

        assert run_and_wrap(FakeOperation(), HashlessModel()).model_hash is None
