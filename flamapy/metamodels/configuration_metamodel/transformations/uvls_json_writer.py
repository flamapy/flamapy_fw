import json

from flamapy.core.transformations.model_to_text import ModelToText
from flamapy.core.models import VariabilityModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration



class UVLSJSONWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'uvl.json'

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path: str = path
        self._configuration: Configuration = source_model

    def transform(self) -> str:
        elements = {'config': self._configuration.elements}
        with open(self._path, "w", encoding="utf-8") as file:
            json.dump(elements, file, ensure_ascii=False, indent=4)
