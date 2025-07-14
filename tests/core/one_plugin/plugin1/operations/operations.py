from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation


class Operation1(Operation):
    def execute(self, model: VariabilityModel) -> "Operation":
        return self

    def get_result(self) -> str:
        return "123456"
