from abc import abstractmethod
from typing import Any

from famapy.core.operations import Operation


class ErrorDiagnosis(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_diagnosis_messages(self) -> list[Any]:
        pass
