from abc import abstractmethod

from flamapy.core.models import VariabilityModel
from flamapy.core.transformations import Transformation


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
