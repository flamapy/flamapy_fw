from famapy.core.models import VariabilityModel
from famapy.core.operations import Operation


class Operation1(Operation):

    def execute(self, model: VariabilityModel) -> 'Operation':
        return self

    def get_result(self) -> str:
        return '123456'
