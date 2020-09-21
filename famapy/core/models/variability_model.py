from abc import ABC, abstractmethod


class VariabilityModel(ABC):

    @staticmethod
    @abstractmethod
    def get_extension() -> str:
        """ Plugin file extension """
