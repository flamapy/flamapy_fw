import csv
import ast
from typing import Any
import pathlib

from flamapy.core.transformations.text_to_model import TextToModel
from flamapy.core.exceptions import ConfigurationNotFound

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


class ConfigurationBasicReader(TextToModel):
    """Reads a configuration from a csvconf file and transforms it into a Configuration model.
    
    The csvconf file should have two columns (separated by commas):
    - The first column contains the element names (e.g., features).
    - The second column contains the values for those elements.
    Values can be of various types, including Boolean, numeric, strings, lists, or dictionaries.

    If the path is a directory, it will read all csvconf files in that directory and concatenate
    their configurations into a single Configuration object.
    This allows for managing multiple configurations associated with variability models split in
    several files (e.g., imports in UVL models).

    If the csvconf file or directory does not exist, it raises a ConfigurationNotFound exception.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'csvconf'

    def __init__(self, path: str) -> None:
        self._path: str = path

    def transform(self) -> Configuration:
        path = pathlib.Path(self._path)
        if path.is_file():
            return self.get_configuration_from_csv(path)
        elif path.is_dir():
            return self.get_configuration_from_directory(path)
        else:
            raise ConfigurationNotFound

    def get_configuration_from_csv(self, path: pathlib.Path) -> Configuration:
        elements = {}
        with open(path, 'r', encoding='utf-8') as csvfile:
            csv_reader = list(csv.reader(csvfile))
            for row in csv_reader:
                element = row[0]
                value = convert(row[1])
                elements[element] = value
        return Configuration(elements)
    
    def get_configuration_from_directory(self, directory: pathlib.Path) -> Configuration:
        """Reads all CSV files in a directory and returns a Configuration object as
        result of concatenating all configurations."""
        elements = {}
        for filepath in directory.rglob('*.csvconf'):
            if filepath.is_file():
                config = self.get_configuration_from_csv(filepath)
                elements.update(config.elements)
        return Configuration(elements)


def convert(value: str) -> Any:
    """
    Converts a string to the most appropriate Python type.
    
    Handles:
    - Boolean values like 'true', 'FALSE', etc.
    - Numeric values (int, float)
    - Python literals (lists, dicts, tuples, None)
    - Returns the original string if no conversion is possible
    """
    stripped = value.strip()
    # Empty or whitespace-only → None
    if stripped == '':
        return None

    # Normalize and check for boolean values
    val_lower = value.strip().lower()
    if val_lower == 'true':
        return True
    if val_lower == 'false':
        return False

    try:
        # Try to evaluate safe Python literals (e.g. numbers, lists, tuples)
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # If evaluation fails, return the string itself
        return value
