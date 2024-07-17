from flamapy.core.operations import Satisfiable
from flamapy.core.models.variability_model import VariabilityModel


class Operation1(Satisfiable):
    def __init__(self):
        pass

    def execute(self, model: VariabilityModel) -> Satisfiable:
        return Operation1()

    def is_satisfiable(self) -> bool:
        return True

    def get_result(self):
        return ''
