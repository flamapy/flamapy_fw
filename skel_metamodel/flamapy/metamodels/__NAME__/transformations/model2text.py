from flamapy.core.transformations import ModelToText

from flamapy.metamodels.__NAME___metamodel.models.models import __NAME__Model


class __NAME__ModelToText(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return '__EXT__'

    def __init__(self, path: str, model: __NAME__Model):
        self.path = path
        self.model = __NAME__Model()

    def transform(self) -> str:
        # TODO: insert your code here
        return self.path
