from abc import ABC, abstractmethod

from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToModel(Transformation):
    EXT_SRC = ''
    EXT_DST = ''

    @abstractmethod
    def __init__(self, orig: VariabilityModel, dst: VariabilityModel):
        pass

    @abstractmethod
    def transform(self):
        pass
