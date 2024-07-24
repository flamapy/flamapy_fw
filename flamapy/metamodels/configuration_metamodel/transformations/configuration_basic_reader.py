import csv

from flamapy.core.transformations.text_to_model import TextToModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.utils import file_exists
from flamapy.core.exceptions import ConfigurationNotFound


class ConfigurationBasicReader(TextToModel):
    @staticmethod
    def get_source_extension() -> str:
        return 'csvconf'

    def __init__(self, path: str) -> None:
        self._path = path

    def transform(self) -> Configuration:
        csv_reader = self.get_configuration_from_csv(self._path)
        elements = {}
        for row in csv_reader:
            # Assuming that row[1] is supposed to represent a boolean value
            # Convert 'true'/'false' strings to actual boolean values
            elements[row[0]] = row[1].lower() == 'true'
        return Configuration(elements)

    def get_configuration_from_csv(self, path: str) -> list[list[str]]:
        # Returns a list of list
        if not file_exists(path):
            raise ConfigurationNotFound

        with open(path, 'r', encoding='utf-8') as csvfile:
            csvreader = list(csv.reader(csvfile))

        return csvreader
