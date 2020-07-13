from abc import ABC, abstractmethod

from famapy.core.operations.AbstractOperation import Operation


class ProductsOperation(Operation):
    @abstractmethod
    def getProducts(self):
        pass
