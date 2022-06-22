from abc import ABC, abstractmethod


class VariabilityModel(ABC):

    @staticmethod
    @abstractmethod
    def get_extension() -> str:
        """ Plugin file extension """


class VariabilityElement():
    def __init__(self, name: str) -> None:
        self.name = name
