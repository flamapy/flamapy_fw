from abc import ABC, abstractmethod
from core.operations.AbstractOperation import Operation

class Valid(Operation):
    @abstractmethod
    def isValid(self):
        pass