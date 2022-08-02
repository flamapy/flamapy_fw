from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class ErrorDetection(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_errors_messages(self) -> list[Any]:
        pass
