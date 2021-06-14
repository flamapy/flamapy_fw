from abc import abstractmethod
from typing import Any

from famapy.core.models import Configuration
from famapy.core.operations import Operation


class Filter(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def get_filter_products(self) -> list[Any]:
        pass
