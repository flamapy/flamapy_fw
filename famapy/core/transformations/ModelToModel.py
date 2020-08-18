from abc import ABC, abstractmethod

from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToModel(Transformation):
    EXT_SRC = ''
    EXT_DST = ''
    #TODO: aqui las extensiones debes sacarlas de los tipos del metamodelo orig y dst

    @abstractmethod
    def __init__(self, orig: VariabilityModel, dst: VariabilityModel):
        pass

    @abstractmethod
    def transform(self):
        pass
