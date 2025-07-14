from flamapy.core.transformations import (
    ModelToModel,
    ModelToText,
    TextToModel,
)

from .variability_model import ExampleModel


class M2M(ModelToModel):
    @staticmethod
    def get_source_extension() -> str:
        return "ext2"

    @staticmethod
    def get_destination_extension() -> str:
        return "ext3"

    def __init__(self, source_model: ExampleModel) -> None:
        pass

    def transform(self) -> ExampleModel:
        return ExampleModel()


class M2T(ModelToText):
    pass


class T2M(TextToModel):
    pass
