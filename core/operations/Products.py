from abc import ABC, abstractmethod
from core.operations.AbstractOperation import Operation

class ProductsOperation(Operation):
    @abstractmethod
    def getProducts(self):
        pass