from flamapy.core.operations import (
    Operation,
    OperationDescriptor,
    Input,
    collect_descriptors,
)


class _CountInterface(Operation):
    """Stand-in for an operation interface that declares a facade descriptor."""

    facade = OperationDescriptor(
        name='configurations_number',
        operation='ConfigurationsNumber',
        default_backend='bdd',
        inputs=(Input('backend', str, 'bdd'),),
    )

    def execute(self, model):  # pragma: no cover - not run
        return self

    def get_result(self):  # pragma: no cover - not run
        return 0


class _BddCount(_CountInterface):
    """A concrete backend impl that inherits the interface descriptor."""


class _SatCount(_CountInterface):
    """Another backend impl, also inheriting the same descriptor."""


class _NoDescriptor(Operation):
    def execute(self, model):  # pragma: no cover
        return self

    def get_result(self):  # pragma: no cover
        return None


def test_descriptor_fields_and_needs_backend():
    d = OperationDescriptor(name='n', operation='Op', default_backend='sat')
    assert d.needs_backend is True
    assert OperationDescriptor(name='n', operation='Op').needs_backend is False  # runs on fm


def test_collect_dedupes_by_public_name_across_backends():
    collected = collect_descriptors([_BddCount, _SatCount, _NoDescriptor])
    assert set(collected) == {'configurations_number'}
    descriptor = collected['configurations_number']
    assert descriptor.operation == 'ConfigurationsNumber'
    assert descriptor.default_backend == 'bdd'
    assert descriptor.inputs[0].name == 'backend'


def test_operations_without_a_descriptor_are_ignored():
    assert collect_descriptors([_NoDescriptor]) == {}
