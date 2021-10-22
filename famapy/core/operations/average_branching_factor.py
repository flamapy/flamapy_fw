from abc import abstractmethod

from famapy.core.operations import Operation


class AverageBranchingFactor(Operation):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_average_branching_factor(self) -> float:
        pass