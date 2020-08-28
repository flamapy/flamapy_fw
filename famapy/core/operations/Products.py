from famapy.core.operations.AbstractOperation import Operation


class Products(Operation):

    def __init__(self):
        self.products = list()

    def getProducts(self) -> list:
        return self.products
