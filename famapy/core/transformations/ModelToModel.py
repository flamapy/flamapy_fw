from abc import ABC, abstractmethod

from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToModel(Transformation):

    @abstractmethod
    def __init__(self, orig: VariabilityModel, dst: VariabilityModel):
        pass

    @abstractmethod
    def transform(self):
        pass