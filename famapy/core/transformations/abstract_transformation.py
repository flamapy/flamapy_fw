from abc import ABC, abstractmethod

from typing import Any


class Transformation(ABC):

    @abstractmethod
    def transform(self) -> Any:
        pass
