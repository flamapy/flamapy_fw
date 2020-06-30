from abc import ABC, abstractmethod
from AbstractOperation import Operation

class ValidOperation(Operation):
    @abstractmethod
    def isValid(self):
        pass