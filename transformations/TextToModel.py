from abc import ABC, abstractmethod
from AbstractTransformation import Transformation

class ModelToModelTransformation(Transformation):
    @abstractmethod
    def transform(self,Metamodel):
        pass