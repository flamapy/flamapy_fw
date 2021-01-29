from abc import ABC, abstractmethod


class Configuration(ABC):

    @abstractmethod
    def __init__(self, elements: list):
        self.elements = elements
