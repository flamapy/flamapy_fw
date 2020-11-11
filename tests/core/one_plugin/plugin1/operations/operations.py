from famapy.core.operations import Operation

from one_plugin.plugin1.models.variability_model import ExampleModel


class Operation1(Operation):

    def execute(self, model: ExampleModel) -> Operation:
        return self

    def get_result(self) -> str:
        return '123456'
