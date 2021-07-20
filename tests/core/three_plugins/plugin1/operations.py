from famapy.core.operations import Operation
from famapy.core.models.variability_model import VariabilityModel


class Operation1(Operation):
    def execute(self, model: VariabilityModel) -> 'Operation':
        return Operation1()

    def get_result(self):
        return ''
