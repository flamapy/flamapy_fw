from abc import abstractmethod

from famapy.core.operations import Operation


class DeadFeatures(Operation):

    @abstractmethod
    def get_dead_features(self) -> bool:
        pass
