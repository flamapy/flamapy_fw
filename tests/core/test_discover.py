import pytest

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
