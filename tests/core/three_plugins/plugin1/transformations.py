from flamapy.core.transformations import (
    ModelToText,
    TextToModel,
)

from .variability_model import ExampleModel


class M2T(ModelToText):
    pass


class T2M(TextToModel):
    @staticmethod
    def get_source_extension() -> str:
        return "xml"

    def __init__(self, path: str) -> None:
        pass

    def transform(self):
        return ExampleModel()
