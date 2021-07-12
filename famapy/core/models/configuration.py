from typing import Any


class Configuration():
    """A configuration is a selection of elements in a variability model.

    It is represented as a dictionary of elements of Any type -> bool.
    """

    def __init__(self, elements: dict[Any, bool]) -> None:
        self.elements = elements

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Configuration):
            return self.elements == other.elements
        return False

    def __hash__(self) -> int:
        return hash(frozenset(self.elements.items()))

    def __str__(self) -> str:
        return str(self.elements)
