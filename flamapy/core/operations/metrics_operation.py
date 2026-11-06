from abc import abstractmethod, ABCMeta
import logging
import json

from typing import Any, Optional, Collection, Type

from flamapy.core.transformations.model_to_model import ModelToModel
from flamapy.core.operations import Operation
from flamapy.core.models import VariabilityModel

LOGGER = logging.getLogger("Metrics")


class Metrics(Operation, metaclass=ABCMeta):
    """This is intended to host a set of metrics calculations for a variability model.

    This abstract class will recruit all its implementations and agregate the results
    """

    filter: Optional[list[str]] = None

    def __init__(self) -> None:
        self.model: Optional[VariabilityModel] = None
        self.result: list[dict[str, Any]] = []

    @abstractmethod
    def calculate_metamodel_metrics(self, model: VariabilityModel) -> list[dict[str, Any]]:
        """Return a list of metrics for each metamodel."""

    @property
    @abstractmethod
    def model_type_extension(self) -> str:
        """Return the model type extension for the specific metric."""

    def only_these_metrics(self, filter_metrics: list[str]) -> None:
        self.filter = filter_metrics

    def execute(self, model: VariabilityModel) -> "Metrics":
        """Collect the metrics of every installed metamodel the model can reach.

        Each `Metrics` subclass works on one metamodel. The model is taken to it directly when
        it already is of that metamodel, through its source model (the ``original_model`` a
        transformation attaches) when that is, or through a model-to-model transformation from
        either; so executing a backend's metrics (e.g. on a SAT model) reports the same set as
        executing them on the source feature model. Metamodels with no route are skipped with
        a warning.
        """
        self.model = model
        for subclass in Metrics.__subclasses__():
            sub_metric = subclass()
            sub_metric.filter = self.filter
            dest_model = self._model_for(model, sub_metric.model_type_extension)
            if dest_model is None:
                LOGGER.warning("No transformation from %r to %r: its metrics are skipped",
                               model.__class__.get_extension(), sub_metric.model_type_extension)
                continue
            self.result.extend(sub_metric.calculate_metamodel_metrics(dest_model))
        return self

    @classmethod
    def _model_for(cls, model: VariabilityModel, extension: str) -> Optional[VariabilityModel]:
        """The model as the given metamodel: itself, its source model, or a transformation of
        either; None when there is no route."""
        candidates = [model]
        original = getattr(model, 'original_model', None)
        if isinstance(original, VariabilityModel):
            candidates.append(original)
        for candidate in candidates:
            if candidate.__class__.get_extension() == extension:
                return candidate
        for candidate in candidates:
            m_to_m = cls._search_transformations(candidate.__class__.get_extension(), extension)
            if m_to_m is not None:
                return m_to_m(candidate).transform()
        return None

    @staticmethod
    def _search_transformations(orig: str, dest: str) -> Optional[Type[ModelToModel]]:
        # Walk the whole subclass tree: transformations may inherit ModelToModel
        # indirectly (e.g. through CacheableModelToModel).
        pending = list(ModelToModel.__subclasses__())
        while pending:
            m_to_m = pending.pop()
            pending.extend(m_to_m.__subclasses__())
            if m_to_m.get_source_extension() == orig and m_to_m.get_destination_extension() == dest:
                return m_to_m
        return None

    def get_result(self) -> list[dict[str, Any]]:
        return self.result

    def get_result_json(self) -> str:
        return json.dumps(self.get_result(), indent=4)

    @staticmethod
    def get_ratio(
        collection1: Collection[Any], collection2: Collection[Any], precision: int = 4
    ) -> float:
        if not collection1 and not collection2:
            # Handle case where both collections are empty
            return 0.0
        if not collection2:
            return 0.0
        return float(round(len(collection1) / len(collection2), precision))

    @staticmethod
    def construct_result(  # noqa: PLR0913, PLR0917
        name: str,
        doc: str,
        result: Any,
        size: Optional[int] = None,
        ratio: Optional[float] = None,
        parent: Optional[Any] = None,
        level: int = 0,
    ) -> dict[str, Any]:
        # pylint: disable=too-many-arguments
        """Constructs a dictionary with named keys from the provided values.

        Arguments:
            name: The property name.
            doc: The description of the property.
            result: The value(s).
            size (optional): The length of the values (number of values).
            ratio (optional): The percentage of values with regards the total number of possible
            values.
            parent (optional): The parent metrics of which this metric is based on
            (for organization purposes).
            level (optional): The number of ancestors of this metrics (for organization purposes).
        """
        return {
            "name": name,
            "documentation": doc,
            "result": result,
            "size": size,
            "ratio": ratio,
            "parent": parent,
            "level": level,
        }
