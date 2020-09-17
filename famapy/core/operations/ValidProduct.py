from famapy.core.operations.AbstractOperation import Operation


class ValidProduct(Operation):

    def __init__(self):
        self.res = False

    def setConfiguration(self,configuration:'Configuration'):
        self.configuration=configuration
    
    def isValid(self) -> bool:
        return self.res
    
