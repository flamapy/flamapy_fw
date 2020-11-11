import pytest
from pytest_mock import mock

from famapy.core.discover import DiscoverMetamodels
from famapy.core.models import VariabilityModel


class TestDiscover:

    def test_discover(self):
        discover = DiscoverMetamodels()
        assert len(discover.plugins) == 0

    def test_invalid_model_implementation(self):
        with pytest.raises(TypeError) as error:
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

    def test_discover_one_plugin(self):
        import one_plugin
        with mock.patch.object(
            DiscoverMetamodels,
            '_get_modules_from_plugin_paths',
            return_value=[one_plugin]
        ) as mock_func:
            discover = DiscoverMetamodels()
            assert len(discover.plugins) == 1
            assert len(discover.plugins.get('one_plugin.plugin1').get('operations')) == 1
            assert len(discover.plugins.get('one_plugin.plugin1').get('transformations')) == 3

    def test_discover_two_plugins(self):
        import two_plugins
        with mock.patch.object(DiscoverMetamodels,
            '_get_modules_from_plugin_paths',
            return_value=[two_plugins]
        ) as mock_func:
            discover = DiscoverMetamodels()
            assert len(discover.plugins) == 2
            assert discover.plugins.get('two_plugins.plugin1').get('operations', None) == None
            assert discover.plugins.get('two_plugins.plugin1').get('transformations', None) == None
            assert discover.plugins.get('two_plugins.plugin2').get('operations', None) == None
            assert discover.plugins.get('two_plugins.plugin2').get('transformations', None) == None

    def test_discover_complex_plugin(self):
        import complex_plugin
        with mock.patch.object(
            DiscoverMetamodels,
            '_get_modules_from_plugin_paths',
            return_value=[complex_plugin]
        ) as mock_func:
            discover = DiscoverMetamodels()
            assert len(discover.plugins) == 1
            assert len(discover.plugins.get('complex_plugin.plugin1').get('operations')) == 1
            assert len(discover.plugins.get('complex_plugin.plugin1').get('transformations')) == 3


class TestDiscoverApplyFunctions:

    def test_discover_apply_functions(self):
        import one_plugin
        from one_plugin.plugin1.models.variability_model import VariabilityModel
        with mock.patch.object(
            DiscoverMetamodels,
            '_get_modules_from_plugin_paths',
            return_value=[one_plugin]
        ) as mock_func:
            discover = DiscoverMetamodels()

            variability_model = discover.use_transformation_t2m(src='file.ext', dst='ext')
            operation = discover.use_operation(src=variability_model, operation='Operation1')

            assert isinstance(variability_model, VariabilityModel)
            assert operation.get_result() == '123456'
