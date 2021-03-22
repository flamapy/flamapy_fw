from abc import abstractmethod

from famapy.core.operations import Operation


class CountLeafs(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_number_of_leafs(self) -> int:
        pass