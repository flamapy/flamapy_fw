from types import ModuleType

import pytest

from flamapy.core.exceptions import NoCompatibleBackendError
from flamapy.core.manifest import OperationCapability, PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.core.planner import Plan, PlannerPolicy, plan
from flamapy.core.plugins import Plugin, Plugins

BOOLEAN = LanguageLevel(MajorLevel.BOOLEAN, set())
TYPED = LanguageLevel(MajorLevel.TYPE, set())

EDGES = [('fm', 'pysat'), ('fm', 'bdd'), ('fm', 'z3'), ('fm', 'sharpsat'), ('fm', 'dnnf'), ('bdd', 'x2')]


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


# --- cost curves, plugin-wide limits, transformation costs, availability, exactness ---------


def _manifest_plugin(name, extension, manifest, op_names=('satisfiable',), default_backend=None):
    module = ModuleType(f'flamapy.metamodels.{name}')
    module.MANIFEST = manifest
    plugin = Plugin(module=module)
    for op_name in op_names:
        descriptor = OperationDescriptor(
            name=op_name, operation='X', doc='d', returns='Any', default_backend=default_backend)
        plugin.append_operation(type(f'{name}_{op_name}', (), {'facade': descriptor}))
    return plugin


def test_cost_curve_picks_the_size_bin():
    curve = PluginManifest(
        name='bdd', extension='bdd', supported_level=BOOLEAN, transformation_cost=0,
        operations={'satisfiable': OperationCapability(cost_curve=((100, 1), (1000, 50)))})
    flat = PluginManifest(
        name='pysat', extension='pysat', supported_level=BOOLEAN, transformation_cost=0,
        operations={'satisfiable': OperationCapability(cost=10)})
    plugins = [_manifest_plugin('bdd', 'bdd', curve), _manifest_plugin('pysat', 'pysat', flat)]
    assert _plan(plugins, n_features=50).plugin_name == 'bdd'      # 1 < 10
    assert _plan(plugins, n_features=500).plugin_name == 'pysat'   # 50 > 10
    assert _plan(plugins, n_features=5000).plugin_name == 'pysat'  # beyond the curve: last bin


def test_plugin_wide_max_features_applies_to_undeclared_operations():
    compiled = PluginManifest(name='bdd', extension='bdd', supported_level=BOOLEAN,
                              max_features=300, transformation_cost=0,
                              operations={'satisfiable': OperationCapability(cost=1)})
    fallback = PluginManifest(name='pysat', extension='pysat', supported_level=BOOLEAN,
                              transformation_cost=0)
    plugins = [_manifest_plugin('bdd', 'bdd', compiled, op_names=('satisfiable', 'sampling')),
               _manifest_plugin('pysat', 'pysat', fallback, op_names=('satisfiable', 'sampling'))]
    assert _plan(plugins, operation='sampling', n_features=100).plugin_name == 'bdd'
    assert _plan(plugins, operation='sampling', n_features=1000).plugin_name == 'pysat'
    assert _plan(plugins, operation='satisfiable', n_features=1000).plugin_name == 'pysat'


def test_transformation_cost_is_charged_per_plugin_and_waived_for_built_models():
    bdd = PluginManifest(name='bdd', extension='bdd', supported_level=BOOLEAN,
                         transformation_cost=1000,
                         operations={'satisfiable': OperationCapability(cost=1)})
    pysat = PluginManifest(name='pysat', extension='pysat', supported_level=BOOLEAN,
                           transformation_cost=10,
                           operations={'satisfiable': OperationCapability(cost=5)})
    plugins = [_manifest_plugin('bdd', 'bdd', bdd), _manifest_plugin('pysat', 'pysat', pysat)]
    fresh = _plan(plugins)
    assert fresh.plugin_name == 'pysat' and fresh.estimated_cost == 15
    built = _plan(plugins, available_models={'bdd'})
    assert built.plugin_name == 'bdd' and built.estimated_cost == 1
    assert 'bdd model already built' in built.rationale
    cached = _plan(plugins, artifact_available=lambda ext: ext == 'bdd')
    assert cached.plugin_name == 'bdd' and 'cached artifact for bdd' in cached.rationale


def test_transformation_cost_curve_follows_the_size():
    bdd = PluginManifest(name='bdd', extension='bdd', supported_level=BOOLEAN,
                         transformation_cost_curve=((100, 10), (1000, 5000)),
                         operations={'satisfiable': OperationCapability(cost=0)})
    pysat = PluginManifest(name='pysat', extension='pysat', supported_level=BOOLEAN,
                           transformation_cost=20,
                           operations={'satisfiable': OperationCapability(cost=0)})
    plugins = [_manifest_plugin('bdd', 'bdd', bdd), _manifest_plugin('pysat', 'pysat', pysat)]
    assert _plan(plugins, n_features=50).plugin_name == 'bdd'
    assert _plan(plugins, n_features=500).plugin_name == 'pysat'


def test_default_bonus_still_keeps_the_historical_backend_when_estimates_are_close():
    bdd = PluginManifest(name='bdd', extension='bdd', supported_level=BOOLEAN,
                         transformation_cost=0,
                         operations={'satisfiable': OperationCapability(cost=1)})
    pysat = PluginManifest(name='pysat', extension='pysat', supported_level=BOOLEAN,
                           transformation_cost=0,
                           operations={'satisfiable': OperationCapability(cost=50)})
    plugins = [_manifest_plugin('bdd', 'bdd', bdd, default_backend='sat'),
               _manifest_plugin('pysat', 'pysat', pysat, default_backend='sat')]
    assert _plan(plugins).plugin_name == 'pysat'
    no_bonus = PlannerPolicy(default_backend_bonus=0)
    assert _plan(plugins, policy=no_bonus).plugin_name == 'bdd'


def test_approximate_implementations_need_permission():
    approx = PluginManifest(name='sharpsat', extension='sharpsat', supported_level=BOOLEAN,
                            transformation_cost=0,
                            operations={'satisfiable': OperationCapability(exact=False, cost=1)})
    exact = PluginManifest(name='bdd', extension='bdd', supported_level=BOOLEAN,
                           transformation_cost=0,
                           operations={'satisfiable': OperationCapability(cost=100)})
    plugins = [_manifest_plugin('sharpsat', 'sharpsat', approx), _manifest_plugin('bdd', 'bdd', exact)]
    assert _plan(plugins).plugin_name == 'bdd'
    allowed = _plan(plugins, allow_approximate=True)
    assert allowed.plugin_name == 'sharpsat' and 'approximate' in allowed.rationale
    with pytest.raises(NoCompatibleBackendError, match='allow_approximate'):
        _plan([_manifest_plugin('sharpsat', 'sharpsat', approx)])


def test_unavailable_plugin_is_rejected_with_its_reason():
    missing = PluginManifest(name='dnnf', extension='dnnf', supported_level=BOOLEAN,
                             available=False, unavailable_reason='the d4 binary is not installed')
    plugins = [_manifest_plugin('dnnf', 'dnnf', missing)]
    with pytest.raises(NoCompatibleBackendError, match='d4 binary'):
        _plan(plugins)
