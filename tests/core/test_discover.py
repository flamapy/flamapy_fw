from pytest import raises
from unittest import mock

from famapy.core import discover
from famapy.core.discover import DiscoverMetamodels
from famapy.core.models import VariabilityModel
from famapy.core.plugins import PluginNotFound

import one_plugin
import two_plugins
import complex_plugin


class TestDiscover:

    def test_discover(self):
        search = DiscoverMetamodels()
        assert len(search.plugins) == 0

    def test_invalid_model_implementation(self):
        with raises(TypeError) as error:
            class MyVariabilityModel(VariabilityModel):
                pass
            MyVariabilityModel()
        assert error.typename == 'TypeError'

    def test_valid_model_implementation(self):
        class MyVariabilityModel(VariabilityModel):
            @staticmethod
            def get_extension():
                return 'test'

        instance = MyVariabilityModel()
        assert instance.get_extension() == 'test'


class TestDiscoverWithPlugin:

    @mock.patch.object(discover, 'filter_modules_from_plugin_paths')
    def test_discover_one_plugin(self, mocker):
        mocker.return_value = [one_plugin]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get('amount_plugins') == 1
        assert stats.get('plugin1').get('amount_operations') == 1
        assert stats.get('plugin1').get('amount_transformations') == 3

    @mock.patch.object(discover, 'filter_modules_from_plugin_paths')
    def test_discover_two_plugins(self, mocker):
        mocker.return_value = [two_plugins]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get('amount_plugins') == 2
        assert stats.get('plugin1').get('amount_operations') == 1
        assert stats.get('plugin1').get('amount_transformations') == 3
        assert stats.get('plugin2').get('amount_operations') == 1
        assert stats.get('plugin2').get('amount_transformations') == 3

    @mock.patch.object(discover, 'filter_modules_from_plugin_paths')
    def test_discover_complex_plugin(self, mocker):
        mocker.return_value = [complex_plugin]
        search = DiscoverMetamodels()
        stats = search.plugins.get_stats()
        assert stats.get('amount_plugins') == 1
        assert stats.get('plugin1').get('amount_operations') == 1
        assert stats.get('plugin1').get('amount_transformations') == 3


class TestDiscoverApplyFunctions:

    @mock.patch.object(discover, 'filter_modules_from_plugin_paths')
    def test_discover_apply_functions(self, mocker):
        mocker.return_value = [one_plugin]
        search = DiscoverMetamodels()

        with raises(PluginNotFound) as error:
            search.use_transformation_t2m(src='file.ext', dst='foo')
        assert error.typename == 'PluginNotFound'

        variability_model = search.use_transformation_t2m(
            src='file.ext', dst='ext'
        )
        assert isinstance(variability_model, VariabilityModel)

        operation = search.use_operation(
            src=variability_model,
            operation='Operation'
        )

        assert operation.get_result() == '123456'
