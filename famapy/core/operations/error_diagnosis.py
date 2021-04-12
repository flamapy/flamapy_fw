from abc import abstractmethod

from famapy.core.operations import Operation


class ErrorDiagnosis(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_diagnosis_messages(self) -> list:
        pass
