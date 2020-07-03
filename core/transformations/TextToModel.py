from abc import ABC, abstractmethod
from AbstractTransformation import Transformation

class ModelToTextTransformation(Transformation):
    
    @abstractmethod
    def register(self, extension, metamodel):
        pass

    @abstractmethod
    def transform(self,Metamodel):
        pass