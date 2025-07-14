import tempfile
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


class TestDiscover:
    def test_discover(self):
        search = DiscoverMetamodels()
        assert len(search.plugins) == 1

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
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_discover_one_plugin(self, mocker):
        mocker.return_value = [one_plugin]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 1
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3

    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_discover_two_plugins(self, mocker):
        mocker.return_value = [two_plugins]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 2
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3
        assert stats.get("plugin2").get("amount_operations") == 1
        assert stats.get("plugin2").get("amount_transformations") == 3

    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_discover_complex_plugin(self, mocker):
        mocker.return_value = [complex_plugin]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get("amount_plugins") == 1
        assert stats.get("plugin1").get("amount_operations") == 1
        assert stats.get("plugin1").get("amount_transformations") == 3


class TestDiscoverApplyFunctions:
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def test_discover_apply_functions(self, mocker):
        mocker.return_value = [one_plugin]
        search = DiscoverMetamodels()

        with raises(PluginNotFound) as error:
            search.use_transformation_t2m(src="file.ext", dst="foo")
        assert error.typename == "PluginNotFound"

        variability_model = search.use_transformation_t2m(src="file.ext", dst="ext")
        assert isinstance(variability_model, VariabilityModel)

        operation = search.use_operation(src=variability_model, operation_name="Operation1")

        assert operation.get_result() == "123456"


class TestDiscoverUseOperationFromFile(TestCase):
    @mock.patch.object(discover, "filter_modules_from_plugin_paths")
    def setUp(self, mocker):
        self.filename = tempfile.NamedTemporaryFile(suffix=".xml").name
        mocker.return_value = [three_plugins]
        self.discover = DiscoverMetamodels()

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
