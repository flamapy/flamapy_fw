from abc import abstractmethod

from flamapy.core.models import VariabilityModel
from flamapy.core.transformations import Transformation


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
