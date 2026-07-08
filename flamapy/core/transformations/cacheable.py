"""Mixin for model-to-model transformations whose output can be cached as a file artifact.

A transformation opts in by inheriting :class:`CacheableModelToModel` and implementing the
dump/load pair; :meth:`flamapy.core.plugins.Plugin.use_transformation_m2m` then consults the
artifact cache (when enabled and the source model has a canonical hash) before running the
expensive transformation.
"""
from abc import abstractmethod
from typing import Any

from flamapy.core.models import VariabilityModel
from flamapy.core.transformations.model_to_model import ModelToModel


class CacheableModelToModel(ModelToModel):
    # File extension of the artifact (e.g. 'dddmp', 'nnf').
    artifact_suffix: str = 'artifact'
    # Bump when the artifact format changes so stale cache entries are never loaded.
    artifact_format_version: int = 1

    def cache_options(self) -> dict[str, Any]:
        """Options that change the artifact's content (e.g. encoder or engine choices)."""
        return {}

    @abstractmethod
    def dump_artifact(self, model: VariabilityModel, path: str) -> None:
        """Serialize the transformed model to ``path``."""

    @abstractmethod
    def load_artifact(self, path: str, source_model: VariabilityModel) -> VariabilityModel:
        """Rebuild the transformed model from ``path`` (given the original source model)."""
