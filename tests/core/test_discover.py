import tempfile
import warnings
from importlib.metadata import EntryPoint

import pytest
from pytest import raises
from unittest import TestCase, mock

from flamapy.core import discover
from flamapy.core.exceptions import OperationNotFound
from flamapy.core.discover import DiscoverMetamodels
from flamapy.core.models import VariabilityModel
from flamapy.core.plugins import PluginNotFound

import one_plugin
import two_plugins
import three_plugins
import complex_plugin


def _entry_point(name: str, value: str) -> EntryPoint:
    return EntryPoint(name=name, value=value, group=discover.ENTRY_POINT_GROUP)


class TestDiscover:
    def test_discover(self):
        search = DiscoverMetamodels()
        # fw ships the configuration metamodel; other flamapy distributions installed in
        # the same environment legitimately contribute more plugins.
        assert "configuration_metamodel" in search.plugins.get_plugin_names()

    def test_instance_is_memoized(self):
        DiscoverMetamodels._instance = None
        try:
            assert DiscoverMetamodels.instance() is DiscoverMetamodels.instance()
        finally:
            DiscoverMetamodels._instance = None

    def test_invalid_model_implementation(self):
        with raises(TypeError) as error:

            class MyVariabilityModel(VariabilityModel):
                pass

            MyVariabilityModel()
        assert error.typename == "TypeError"

    def test_valid_model_implementation(self):
        class MyVariabilityModel(VariabilityModel):
            @staticmethod
            def get_extension():
                return "test"

        instance = MyVariabilityModel()
        assert instance.get_extension() == "test"


class TestDiscoverWithPlugin:
    # Plugins are injected as entry points — the canonical registration since 2.7.

    def test_discover_one_plugin(self):
        search = DiscoverMetamodels(
            entry_points=[_entry_point("plugin1", "one_plugin.plugin1")])
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 1
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3

    def test_discover_two_plugins(self):
        search = DiscoverMetamodels(entry_points=[
            _entry_point("plugin1", "two_plugins.plugin1"),
            _entry_point("plugin2", "two_plugins.plugin2"),
        ])
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 2
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3
        assert stats.get("plugin2").get("amount_operations") == 1
        assert stats.get("plugin2").get("amount_transformations") == 3

    def test_discover_complex_plugin(self):
        search = DiscoverMetamodels(
            entry_points=[_entry_point("plugin1", "complex_plugin.plugin1")])
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 1
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3

    def test_duplicate_entry_points_are_deduplicated(self):
        search = DiscoverMetamodels(entry_points=[
            _entry_point("plugin1", "one_plugin.plugin1"),
            _entry_point("plugin1-again", "one_plugin.plugin1"),
        ])
        assert search.plugins.get_stats().get("amount_plugins") == 1

    def test_unloadable_entry_point_is_skipped(self):
        search = DiscoverMetamodels(entry_points=[
            _entry_point("ghost", "does_not_exist.plugin"),
            _entry_point("plugin1", "one_plugin.plugin1"),
        ])
        assert search.plugins.get_stats().get("amount_plugins") == 1


class TestNamespaceScanFallback:
    # The pre-entry-point discovery path: still functional, but deprecated (removed in 3.1).

    @mock.patch.object(discover, "metadata_entry_points")
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_scan_only_plugin_is_found_with_deprecation_warning(self, scan_mock, ep_mock):
        ep_mock.return_value = []
        scan_mock.return_value = [one_plugin]
        with pytest.warns(DeprecationWarning, match="plugin1"):
            search = DiscoverMetamodels()
        assert search.plugins.get_stats().get("amount_plugins") == 1

    @mock.patch.object(discover, "metadata_entry_points")
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_mixed_discovery_unions_and_warns_only_for_scan_only(self, scan_mock, ep_mock):
        ep_mock.return_value = [_entry_point("plugin1", "two_plugins.plugin1")]
        scan_mock.return_value = [two_plugins]
        with pytest.warns(DeprecationWarning) as records:
            search = DiscoverMetamodels()
        assert search.plugins.get_stats().get("amount_plugins") == 2
        messages = [str(record.message) for record in records]
        assert any("plugin2" in message for message in messages)
        assert not any("plugin1'" in message for message in messages)

    @mock.patch.object(discover, "metadata_entry_points")
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_entry_point_only_discovery_does_not_warn(self, scan_mock, ep_mock):
        ep_mock.return_value = [_entry_point("plugin1", "one_plugin.plugin1")]
        scan_mock.return_value = [one_plugin]
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            search = DiscoverMetamodels()
        assert search.plugins.get_stats().get("amount_plugins") == 1


class TestDiscoverApplyFunctions:
    def test_discover_apply_functions(self):
        search = DiscoverMetamodels(
            entry_points=[_entry_point("plugin1", "one_plugin.plugin1")])

        with raises(PluginNotFound) as error:
            search.use_transformation_t2m(src="file.ext", dst="foo")
        assert error.typename == "PluginNotFound"

        variability_model = search.use_transformation_t2m(src="file.ext", dst="ext")
        assert isinstance(variability_model, VariabilityModel)

        operation = search.use_operation(src=variability_model, operation_name="Operation1")

        assert operation.get_result() == "123456"


class TestDiscoverUseOperationFromFile(TestCase):
    def setUp(self):
        self.filename = tempfile.NamedTemporaryFile(suffix=".xml").name
        self.discover = DiscoverMetamodels(entry_points=[
            _entry_point("plugin1", "three_plugins.plugin1"),
            _entry_point("plugin2", "three_plugins.plugin2"),
            _entry_point("plugin3", "three_plugins.plugin3"),
        ])

    def test_discover_use_operation_from_file_with_plugins(self):
        self.discover.use_operation_from_file("Satisfiable", self.filename, "plugin1")
        self.discover.use_operation_from_file("Operation1", self.filename, "plugin1")

    def test_discover_use_operation_from_file_unexist(self):
        with raises(OperationNotFound):
            self.discover.use_operation_from_file("Unexist", self.filename)

    def test_discover_use_operation_from_file_no_step(self):
        self.discover.use_operation_from_file("Satisfiable", self.filename)
        self.discover.use_operation_from_file("Operation1", self.filename)

    def test_discover_use_operation_from_file_one_step(self):
        self.discover.use_operation_from_file("Satisfiable", self.filename)
        self.discover.use_operation_from_file("Operation2", self.filename)

    def test_discover_use_operation_from_file_two_step(self):
        self.discover.use_operation_from_file("Satisfiable", self.filename)
        self.discover.use_operation_from_file("Operation3", self.filename)

    def test_discover_use_operation_from_file_unreachable_way(self):
        filename = tempfile.NamedTemporaryFile(suffix=".xml2").name
        with raises(NotImplementedError):
            self.discover.use_operation_from_file("Operation1", filename)
