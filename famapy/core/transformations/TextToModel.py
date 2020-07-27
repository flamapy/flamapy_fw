from abc import ABC, abstractmethod

from famapy.core.transformations.AbstractTransformation import Transformation


class TextToModel(Transformation):
    EXT_SRC = ''

    @abstractmethod
    def register(self, extension, metamodel):
        pass

    @abstractmethod
    def transform(self):
        pass
