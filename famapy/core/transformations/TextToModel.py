from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation



class TextToModel(Transformation):
    EXT_SRC = 'default'

    def __init__(self, path):
        self.path = path
        self.model = VariabilityModel()

    def transform(self) -> VariabilityModel:
        return self.model
