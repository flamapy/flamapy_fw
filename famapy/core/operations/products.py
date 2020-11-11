from abc import abstractmethod

from famapy.core.operations import Operation


class Products(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_products(self) -> list:
        pass
