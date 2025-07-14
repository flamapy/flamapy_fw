from flamapy.core.operations import Operation
from flamapy.core.models.variability_model import VariabilityModel


class Operation2(Operation):
    def execute(self, model: VariabilityModel) -> "Operation":
        return Operation2()

    def get_result(self):
        return ""
