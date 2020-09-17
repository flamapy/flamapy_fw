from famapy.core.operations.AbstractOperation import Operation


class ValidConfiguration(Operation):

    def __init__(self):
        self.res = False

    def setConfiguration(self,configuration:'Configuration'):
        self.configuration=configuration
    
    def getCommonality(self) -> float:
        return self.res
    
