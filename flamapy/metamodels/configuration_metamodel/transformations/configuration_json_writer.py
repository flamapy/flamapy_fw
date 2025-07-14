import json
from typing import cast

from flamapy.core.transformations.model_to_text import ModelToText
from flamapy.core.models import VariabilityModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class ConfigurationJSONWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'json'

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path: str = path
        self._configuration: Configuration = cast(Configuration, source_model)

    def transform(self) -> str:
        json_str = json.dumps(self._configuration.elements, ensure_ascii=False, indent=4)
        if self._path is not None:
            with open(self._path, 'w', encoding='utf-8') as file:
                file.write(json_str)
        return json_str
