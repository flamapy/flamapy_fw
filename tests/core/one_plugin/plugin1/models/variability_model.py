from flamapy.core.models import VariabilityModel


class ExampleModel(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'ext'
