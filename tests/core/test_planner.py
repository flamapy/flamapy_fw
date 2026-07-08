from types import ModuleType

import pytest

from flamapy.core.exceptions import NoCompatibleBackendError
from flamapy.core.manifest import OperationCapability, PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.planner import Plan, plan
from flamapy.core.plugins import Plugin, Plugins

BOOLEAN = LanguageLevel(MajorLevel.BOOLEAN, set())
TYPED = LanguageLevel(MajorLevel.TYPE, set())

EDGES = [('fm', 'pysat'), ('fm', 'bdd'), ('fm', 'z3'), ('bdd', 'x2')]


def _plugin(name, extension, level, operations=None, op_names=('satisfiable',),
            default_backend='pysat'):
    module = ModuleType(f'flamapy.metamodels.{name}')
    module.MANIFEST = PluginManifest(
        name=name, extension=extension, supported_level=level,
        operations=operations or {})
    plugin = Plugin(module=module)
    for op_name in op_names:
        descriptor = OperationDescriptor(
            name=op_name, operation='X', doc='d', returns='Any',
            default_backend=default_backend)
        plugin.append_operation(type(f'{name}_{op_name}', (), {'facade': descriptor}))
    return plugin


def _plan(plugins, operation='satisfiable', level=BOOLEAN, n_features=10, **kwargs):
    return plan(operation, source_extension='fm', model_level=level,
                n_features=n_features, plugins=Plugins(plugins), m2m_edges=EDGES, **kwargs)


def test_default_backend_bonus_keeps_historical_routing():
    result = _plan([_plugin('pysat', 'pysat', BOOLEAN), _plugin('bdd', 'bdd', BOOLEAN)])
    assert result.plugin_name == 'pysat'
    assert 'historical default backend' in result.rationale
    assert result.alternatives == ('bdd',)


def test_sat_alias_maps_to_pysat_extension():
    # Descriptors say default_backend='sat'; the plugin's extension is 'pysat'.
    result = _plan([_plugin('pysat', 'pysat', BOOLEAN, default_backend='sat'),
                    _plugin('bdd', 'bdd', BOOLEAN, default_backend='sat')])
    assert result.plugin_name == 'pysat'
    assert 'historical default backend' in result.rationale


def test_cost_ordering_without_default_bonus():
    cheap = _plugin('bdd', 'bdd', BOOLEAN,
                    operations={'satisfiable': OperationCapability(cost=10)},
                    default_backend=None)
    costly = _plugin('pysat', 'pysat', BOOLEAN, default_backend=None)
    assert _plan([costly, cheap]).plugin_name == 'bdd'


def test_language_level_filtering():
    result = _plan([_plugin('pysat', 'pysat', BOOLEAN), _plugin('z3', 'z3', TYPED)],
                   level=TYPED)
    assert result.plugin_name == 'z3'


def test_max_features_disqualifies():
    limited = _plugin('bdd', 'bdd', BOOLEAN,
                      operations={'satisfiable': OperationCapability(max_features=300,
                                                                     cost=1)},
                      default_backend=None)
    fallback = _plugin('pysat', 'pysat', BOOLEAN, default_backend=None)
    assert _plan([limited, fallback], n_features=1000).plugin_name == 'pysat'
    assert _plan([limited, fallback], n_features=100).plugin_name == 'bdd'


def test_no_candidates_raises_with_details():
    with pytest.raises(NoCompatibleBackendError, match='pysat'):
        _plan([_plugin('pysat', 'pysat', BOOLEAN)], level=TYPED)


def test_transformation_chain_via_bfs():
    remote = _plugin('x2', 'x2', BOOLEAN, default_backend=None)
    result = _plan([remote])
    assert result.transformation_chain == (('fm', 'bdd'), ('bdd', 'x2'))


def test_unreachable_extension_is_rejected():
    unreachable = _plugin('nowhere', 'nowhere', BOOLEAN, default_backend=None)
    with pytest.raises(NoCompatibleBackendError, match='no transformation path'):
        _plan([unreachable])


def test_artifact_bonus_tips_the_scale():
    first = _plugin('abdd', 'bdd', BOOLEAN, default_backend=None)
    second = _plugin('pysat', 'pysat', BOOLEAN, default_backend=None)
    without = _plan([first, second])
    assert without.plugin_name == 'abdd'  # tie broken by name
    with_artifact = _plan([first, second],
                          artifact_available=lambda ext: ext == 'pysat')
    assert with_artifact.plugin_name == 'pysat'
    assert 'cached artifact' in with_artifact.rationale


def test_deterministic_name_tiebreak():
    result = _plan([_plugin('zeta', 'bdd', BOOLEAN, default_backend=None),
                    _plugin('alpha', 'pysat', BOOLEAN, default_backend=None)])
    assert result.plugin_name == 'alpha'


def test_fm_level_operation_needs_no_chain():
    fm_plugin = _plugin('fm', 'fm', TYPED, op_names=('atomic_sets',),
                        default_backend=None)
    result = _plan([fm_plugin], operation='atomic_sets')
    assert isinstance(result, Plan)
    assert result.transformation_chain == ()
    assert result.target_extension == 'fm'
