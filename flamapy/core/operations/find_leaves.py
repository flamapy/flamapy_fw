from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class FindLeaves(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def find_leaves_list(self) -> list[Any]:
        pass
