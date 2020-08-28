from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToModel(Transformation):
    EXT_SRC = 'default'
    EXT_DST = 'default'

    def __init__(self, model: VariabilityModel):
        self.model_src = model
        self.model_dst = VariabilityModel()

    def transform(self) -> VariabilityModel:
        return self.model_dst
