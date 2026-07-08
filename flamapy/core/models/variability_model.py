from abc import ABC, abstractmethod
from typing import Optional


class VariabilityModel(ABC):
    @staticmethod
    @abstractmethod
    def get_extension() -> str:
        """Plugin file extension"""

    def canonical_hash(self) -> Optional[str]:
        """A stable content hash of the model, for provenance and caching.

        Model classes with a canonical serialization override this (FeatureModel hashes
        its canonical UVL form); the default None means "no canonical form available".
        """
        return None


class VariabilityElement:
    def __init__(self, name: str) -> None:
        self.name = name
