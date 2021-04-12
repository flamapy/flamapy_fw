from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class ErrorDetection(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_errors_messages(self) -> list[Any]:
        pass
