from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToText(Transformation):
    EXT_DST = 'default'

    def __init__(self, path: str, model: VariabilityModel):
        self.path = path
        self.model = model

    def transform(self) -> str:
        return self.path
