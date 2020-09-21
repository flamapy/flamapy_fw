from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelModel

from famapy.metamodels.__NAME___metamodel.models.models import __NAME__Model


class TODOTo__NAME__(ModelToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'TODO'  # TODO: modify source extension

    @staticmethod
    def get_destiny_extension() -> str:
        return '__EXT__'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.destiny_model = __NAME__Model()

    def transform(self) -> __NAME__Model:
        # TODO: insert your code here
        return self.destiny_model
