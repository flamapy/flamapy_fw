from flamapy.core.operations import Valid
from flamapy.core.models.variability_model import VariabilityModel


class Operation1(Valid):
    def __init__(self):
        pass

    def execute(self, model: VariabilityModel) -> Valid:
        return Operation1()

    def is_valid(self) -> bool:
        return True

    def get_result(self):
        return ''
