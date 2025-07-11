import json

from flamapy.core.transformations.model_to_text import ModelToText
from flamapy.core.models import VariabilityModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration



class ConfigurationJSONWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'json'

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path: str = path
        self._configuration: Configuration = source_model

    def transform(self) -> str:
        with open(self._path, "w", encoding="utf-8") as file:
            json.dump(self._configuration.elements, file, ensure_ascii=False, indent=4)
