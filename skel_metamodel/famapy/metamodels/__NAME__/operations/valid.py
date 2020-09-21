from famapy.core.operations import Valid

from famapy.metamodels.__NAME___metamodel.models.models import __NAME__Model


class __NAME__Valid(Valid):

    def __init__(self):
        self.result = False

    def execute(self, model: __NAME__Model) -> '__NAME__Valid':
        # TODO: insert your model code here
        return self.result
