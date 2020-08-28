from famapy.core.transformations.ModelToText import ModelToText
from famapy.metamodels.__NAME___metamodel.models.models import __NAME__Model


class __NAME__ModelToText(ModelToText):
    EXT_DST = '__EXT__'

    def __init__(self, path: str, model: __NAME__Model):
        self.path = path
        self.model = __NAME__Model()

    def transform(self) -> str:
        # TODO: insert your code here
        return super().transform()
