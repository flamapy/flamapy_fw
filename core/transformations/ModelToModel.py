from abc import ABC, abstractmethod

from core.models.VariabilityModel import VariabilityModel
from core.transformations.AbstractTransformation import Transformation


class ModelToModelTransformation(Transformation):
    @abstractmethod
    def __init__(self, model1: VariabilityModel, model2: VariabilityModel):
        pass

    @abstractmethod
    def transform(self):
        pass
