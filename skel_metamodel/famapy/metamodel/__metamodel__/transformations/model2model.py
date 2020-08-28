from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.ModelToModel import ModelModel
from famapy.metamodels.__NAME___metamodel.models.models import __NAME__Model


class FILLTo__NAME__(ModelToModel):
    EXT_SCR = 'fill'  # TODO: modify
    EXT_DST = '__EXT__'

    def __init__(self, model_src: VariabilityModel):
        self.model_src = model_src
        self.model_dst = __NAME__Model()

    def transform(self) -> __NAME__Model:
        # TODO: insert your code here
        return super().transform()
