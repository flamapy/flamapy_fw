from abc import abstractmethod, ABCMeta
import logging
import json 

from typing import Any, Optional, Collection, Type

from flamapy.core.exceptions import FlamaException
from flamapy.core.transformations.model_to_model import ModelToModel
from flamapy.core.operations import Operation
from flamapy.core.models import VariabilityModel

LOGGER = logging.getLogger('Metrics')


class Metrics(Operation, metaclass=ABCMeta):
    """This is intended to host a set of metrics calculations for a variability model.

    This abstract class will recruit all its implementations and agregate the results
    """
    filter: Optional[list[str]] = None
    result: list[dict[str, Any]] = []

    def __init__(self) -> None:
        self.model: Optional[VariabilityModel] = None

    @abstractmethod
    def calculate_metamodel_metrics(self, model: VariabilityModel) -> list[dict[str, Any]]:
        """Return a list of metrics for each metamodel."""  

    @property
    @abstractmethod
    def model_type_extension(self) -> str:
        """Return the model type extension for the specific metric."""

    def only_these_metrics(self, filter_metrics: list[str]) -> None:
        self.filter = filter_metrics 

    def execute(self, model: VariabilityModel) -> 'Metrics':
        self.model = model
        # Identifying all implementations of MetricsOperation

        for subclass in Metrics.__subclasses__(): 
            # We first have to identify the metamodels that are being used and 
            # transform this model to the correspointing metamodel
            metrics_operation = subclass()  # type: ignore

            if self.model.__class__.get_extension() == metrics_operation.model_type_extension:
                # If its the metamodel that math the model, calculate the metrics
                # Then we calculate the metrics for each metamodel
                sub_metric = subclass()  # type: ignore
                sub_metric.filter = self.filter
                self.result.extend(sub_metric.calculate_metamodel_metrics(model))
            else:
                # If not, search a transformation, transform and call the calutation
                m_to_m = self._search_transformations(self.model.__class__.get_extension(), 
                                                      metrics_operation.model_type_extension)
                dest_model = m_to_m(self.model).transform()
                sub_metric = subclass()  # type: ignore
                sub_metric.filter = self.filter
                self.result.extend(sub_metric.calculate_metamodel_metrics(dest_model))
        return self

    def _search_transformations(self, orig: str, dest: str) -> Type[ModelToModel]:
        try:
            for m_to_m in ModelToModel.__subclasses__():
                _orig = m_to_m.get_source_extension()
                _dest = m_to_m.get_destination_extension()
                if (_orig == orig and _dest == dest):
                    return m_to_m
        except FlamaException:
            LOGGER.exception("No transformation found that is required in the Metrics operation")
        raise FlamaException(f"No transformation found for {orig} -> {dest}")

    def get_result(self) -> list[dict[str, Any]]:
        return self.result

    def get_result_json(self) -> str: 
        return json.dumps(self.get_result(), indent=4) 

    @staticmethod
    def get_ratio(collection1: Collection[Any], 
                  collection2: Collection[Any], 
                  precision: int = 4) -> float:
        if not collection1 and not collection2:
            # Handle case where both collections are empty
            return 0.0
        if not collection2:
            return 0.0
        return float(round(len(collection1) / len(collection2), precision))

    @staticmethod
    def construct_result(name: str,
                         doc: str,
                         result: Any, 
                         size: Optional[int] = None, 
                         ratio: Optional[float] = None,
                         parent: Optional[Any] = None,
                         level: int = 0
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
            "level": level
        }
