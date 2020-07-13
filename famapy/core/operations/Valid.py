from abc import ABC, abstractmethod

from famapy.core.operations.AbstractOperation import Operation


class Valid(Operation):
    @abstractmethod
    def isValid(self):
        pass
