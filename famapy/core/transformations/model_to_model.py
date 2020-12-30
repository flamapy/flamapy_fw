from abc import abstractmethod

from famapy.core.models import VariabilityModel
from famapy.core.transformations import Transformation


class ModelToModel(Transformation):

    @staticmethod
    @abstractmethod
    def get_source_extension() -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_destination_extension() -> str:
        pass

    @abstractmethod
    def __init__(self, source_model: VariabilityModel) -> None:
        pass
