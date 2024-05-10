from abc import abstractmethod

from flamapy.core.operations import Operation


class Satisfiable(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def is_satisfiable(self) -> bool:
        pass
