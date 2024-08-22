from typing import Any, Iterator
from flamapy.core.models import VariabilityModel


class Configuration(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'configuration'

    def __init__(self, elements: dict[Any, bool]) -> None:
        self.elements = elements
        self.is_full = False

    def set_full(self, is_full: bool) -> None:
        self.is_full = is_full

    def get_selected_elements(self) -> list[Any]:
        return [e for e in self.elements if self.elements[e]]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Configuration):
            return self.elements == other.elements
        return False

    def __hash__(self) -> int:
        return hash(frozenset(self.elements.items()))

    def __str__(self) -> str:
        return ', '.join([str(e) for e in self.get_selected_elements()])

    def __repr__(self) -> str:
        return f"Configuration({self.elements})"

    def __iter__(self) -> Iterator[Any]:
        return iter(self.elements)
