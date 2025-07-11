import json
import pathlib

from flamapy.core.transformations.text_to_model import TextToModel

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.exceptions import ConfigurationNotFound


class ConfigurationJSONReader(TextToModel):
    """Reads a configuration from a JSON file or directory and transforms it into 
    a Configuration model.

    The JSON file should contain a dictionary where keys are element names (e.g., features)
    and values are the corresponding values for those elements. 
    
    If the path is a directory, it will read all JSON files in that directory and concatenate
    their configurations into a single Configuration object.
    This allows for managing multiple configurations associated with variability models split in
    several files (e.g., imports in UVL models).

    If the JSON file or directory does not exist, it raises a ConfigurationNotFound exception.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'json'

    def __init__(self, path: str) -> None:
        self._path: str = path

    def transform(self) -> Configuration:
        path = pathlib.Path(self._path)
        if path.is_file():
            return self.get_configuration_from_json(path)
        elif path.is_dir():
            return self.get_configuration_from_directory(path)
        else:
            raise ConfigurationNotFound

    def get_configuration_from_json(self, path: pathlib.Path) -> Configuration:
        """Reads a JSON file and returns a Configuration object."""
        with open(path, 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
            elements = json_dict
        return Configuration(elements)
    
    def get_configuration_from_directory(self, directory: pathlib.Path) -> Configuration:
        """Reads all JSON files in a directory and returns a Configuration object as
        result of concatenating all configurations."""
        elements = {}
        for filepath in directory.rglob('*.json'):
            if filepath.is_file():
                config = self.get_configuration_from_json(filepath)
                elements.update(config.elements)
        return Configuration(elements)
