from flamapy.core.transformations import (
    ModelToModel,
    ModelToText,
    TextToModel,
)
from flamapy.core.models import VariabilityModel
from one_plugin.plugin1.models.variability_model import ExampleModel


class M2M(ModelToModel):
    @staticmethod
    def get_source_extension() -> str:
        return 'ext'

    @staticmethod
    def get_destination_extension() -> str:
        return 'ext'

    def __init__(self, source_model: VariabilityModel) -> None:
        self.source_model = source_model

    def transform(self) -> VariabilityModel:
        """ Fake transform for test, return the same value """
        return self.source_model


class M2T(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'ext'

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        pass

    def transform(self) -> ExampleModel:
        return 'example'


class T2M(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'ext'

    def __init__(self, path: str) -> None:
        pass

    def transform(self) -> ExampleModel:
        return ExampleModel()
