from typing import Any, Iterator

from flamapy.core.models import VariabilityModel


class Configuration(VariabilityModel):
    """A class representing a configuration in a variability model.
    
    A configuration is a dictionary of elements (e.g., features) with their values.
    Elements can be of any type, and their values can be also of any type.
    Normally, the values are Boolean to indicate whether the element is selected or not
    in the configuration. However, they can also be other types, such as integers, strings, lists,
    or dictionaries to represent more complex configurations (e.g., sub-configurations).
    
    An element with a value of `False` indicates that it is not selected, otherwise it is selected.
    For instance, a String element with a value of `None` is considered selected, but it has not
    a value assigned to it.
    If an element is not present in the configuration, it is considered undecided.
    
    A configuration can be partial or full.
    A full configuration considers that all elements have been decided.
    A partial configuration may have some elements undecided.
    The `is_full` attribute indicates whether the configuration is full or partial.
    """

    @staticmethod
    def get_extension() -> str:
        return 'configuration'

    def __init__(self, elements: dict[Any, Any]) -> None:
        self.elements: dict[Any, Any] = elements
        self.is_full: bool = False

    def set_full(self, is_full: bool) -> None:
        self.is_full = is_full

    def get_selected_elements(self) -> list[Any]:
        """Get the list of selected elements in the configuration."""
        return [e for e in self.elements if self.is_selected(e)]

    def is_selected(self, element: Any) -> bool:
        """Check if an element is selected in the configuration.
        
        An element is considered selected if it exists in the configuration
        and its value is not False.
        """
        return element in self.elements and (not isinstance(self.elements[element], bool) or 
                                             self.elements[element])
    
    def get_value(self, element: Any) -> Any:
        return self.elements[element]

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
