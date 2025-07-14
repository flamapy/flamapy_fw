import io
import csv
from typing import cast

from flamapy.core.transformations.model_to_text import ModelToText
from flamapy.core.models import VariabilityModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class ConfigurationBasicWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'csvconf'

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path: str = path
        self._configuration: Configuration = cast(Configuration, source_model)

    def transform(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        for key, value in self._configuration.elements.items():
            writer.writerow([key, value])
        csv_content = output.getvalue()
        output.close()
        if self._path is not None:
            with open(self._path, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)
        return csv_content
