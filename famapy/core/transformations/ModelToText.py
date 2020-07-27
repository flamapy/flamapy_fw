from abc import ABC, abstractmethod

from famapy.core.transformations.AbstractTransformation import Transformation


class ModelToText(Transformation):
    EXT_DST = ''

    @abstractmethod
    def register(self, path, metamodel):
        pass

    @abstractmethod
    def transform(self):
        pass
