from abc import abstractmethod

from famapy.core.models import VariabilityModel
from famapy.core.transformations import Transformation


class TextToModel(Transformation):

    @staticmethod
    @abstractmethod
    def get_source_extension() -> str:
        pass

    @abstractmethod
    def __init__(self, path: str) -> None:
        pass

    @abstractmethod
    def transform(self) -> VariabilityModel:
        pass
