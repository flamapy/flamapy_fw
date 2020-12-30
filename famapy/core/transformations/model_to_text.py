from abc import abstractmethod

from famapy.core.models import VariabilityModel
from famapy.core.transformations import Transformation


class ModelToText(Transformation):

    @staticmethod
    @abstractmethod
    def get_destination_extension() -> str:
        pass

    @abstractmethod
    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        pass

    @abstractmethod
    def transform(self) -> str:
        pass
