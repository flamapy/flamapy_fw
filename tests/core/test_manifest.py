from importlib.metadata import EntryPoint

from flamapy.core import discover
from flamapy.core.discover import DiscoverMetamodels
from flamapy.core.manifest import (
    DEFAULT_COST,
    OperationCapability,
    PluginManifest,
    synthesized_manifest,
)
from flamapy.core.models.language_level import (
    ALL_MINOR_LEVELS,
    LanguageLevel,
    MajorLevel,
    MinorLevel,
)

import one_plugin  # noqa: F401  (makes the synthetic package importable by entry point)


BOOLEAN = LanguageLevel(MajorLevel.BOOLEAN, set())
TYPED_FULL = LanguageLevel(MajorLevel.TYPE, set(ALL_MINOR_LEVELS))


class TestSupports:
    def test_higher_major_supports_lower(self):
        manifest = PluginManifest(name='x', supported_level=TYPED_FULL)
        assert manifest.supports(BOOLEAN)

    def test_lower_major_rejects_higher(self):
        manifest = PluginManifest(name='x', supported_level=BOOLEAN)
        assert not manifest.supports(LanguageLevel(MajorLevel.TYPE, set()))

    def test_minor_levels_must_be_covered(self):
        cardinality = LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY})
        assert not PluginManifest(name='x', supported_level=BOOLEAN).supports(cardinality)
        assert PluginManifest(
            name='x',
            supported_level=LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY}),
        ).supports(cardinality)


class TestCapability:
    def test_declared_operation_capability(self):
        manifest = PluginManifest(
            name='x', operations={'sampling': OperationCapability(exact=False, cost=5)})
        assert manifest.capability('sampling') == OperationCapability(exact=False, cost=5)

    def test_undeclared_operation_gets_default(self):
        manifest = PluginManifest(name='x', default_cost=7)
        capability = manifest.capability('anything')
        assert capability.exact and capability.max_features is None and capability.cost == 7


class TestPluginManifestDiscovery:
    def _plugin(self):
        search = DiscoverMetamodels(entry_points=[EntryPoint(
            name='plugin1', value='one_plugin.plugin1', group=discover.ENTRY_POINT_GROUP)])
        return search.plugins.get_plugin_by_name('plugin1')

    def test_missing_manifest_synthesizes_conservative_default(self):
        manifest = self._plugin().manifest
        assert manifest.name == 'plugin1'
        assert manifest.extension == 'ext'
        assert manifest.supported_level == BOOLEAN
        assert manifest.default_cost == DEFAULT_COST

    def test_synthesized_manifest_helper(self):
        manifest = synthesized_manifest('anything')
        assert manifest.supported_level == BOOLEAN and manifest.extension is None

    def test_declared_manifest_is_used(self):
        plugin = self._plugin()
        declared = PluginManifest(name='declared', supported_level=TYPED_FULL)
        plugin.module.MANIFEST = declared
        try:
            assert plugin.manifest is declared
        finally:
            del plugin.module.MANIFEST


class TestCostsAndLimits:
    def test_cost_curve_bins_and_extrapolation(self):
        capability = OperationCapability(cost=7, cost_curve=((50, 1), (500, 20)))
        assert capability.cost_at(10) == 1
        assert capability.cost_at(50) == 1
        assert capability.cost_at(51) == 20
        assert capability.cost_at(10_000) == 20
        assert OperationCapability(cost=7).cost_at(10_000) == 7

    def test_plugin_wide_max_features_applies_to_undeclared_and_unlimited_operations(self):
        manifest = PluginManifest(
            name='x', max_features=300,
            operations={'sampling': OperationCapability(cost=5),
                        'configurations': OperationCapability(max_features=30)})
        assert manifest.capability('anything').max_features == 300
        assert manifest.capability('sampling') == OperationCapability(cost=5, max_features=300)
        assert manifest.capability('configurations').max_features == 30

    def test_transformation_cost_curve(self):
        manifest = PluginManifest(name='x', transformation_cost=10,
                                  transformation_cost_curve=((100, 5), (1000, 500)))
        assert manifest.transformation_cost_at(10) == 5
        assert manifest.transformation_cost_at(1000) == 500
        assert PluginManifest(name='y').transformation_cost_at(1000) == 100

    def test_availability_defaults(self):
        assert PluginManifest(name='x').available
        manifest = PluginManifest(name='x', available=False, unavailable_reason='no binary')
        assert not manifest.available and manifest.unavailable_reason == 'no binary'
