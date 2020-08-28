from famapy.core.operations.AbstractOperation import Operation


class Valid(Operation):

    def __init__(self):
        self.res = False

    def isValid(self) -> bool:
        return self.res
