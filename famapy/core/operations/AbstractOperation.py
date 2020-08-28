from famapy.core.models.VariabilityModel import VariabilityModel


class Operation():

    def execute(self, model: VariabilityModel) -> 'Operation':
        return self
