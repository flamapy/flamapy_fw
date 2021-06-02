from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class ProductsNumber(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_products_number(self) -> int:
        pass
