from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class Products(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_products(self) -> list[Any]:
        pass
