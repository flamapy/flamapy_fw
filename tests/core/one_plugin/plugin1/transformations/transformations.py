from famapy.core.transformations import (
    ModelToModel,
    ModelToText,
    TextToModel,
)

from one_plugin.plugin1.models.variability_model import ExampleModel


class M2M(ModelToModel):
    pass


class M2T(ModelToText):
    pass


class T2M(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'ext'

    def __init__(self, path: str) -> None:
        pass

    def transform(self) -> ExampleModel:
        return ExampleModel()
