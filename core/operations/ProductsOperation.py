from abc import ABC, abstractmethod
from AbstractOperation import Operation

class ProductsOperation(Operation):
    @abstractmethod
    def getProducts(self):
        pass