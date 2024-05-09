from abc import abstractmethod
import logging
import json 

from typing import Any, Optional, Collection

from flamapy.core.exceptions import FlamaException
from flamapy.core.transformations.model_to_model import ModelToModel
from flamapy.core.operations import Operation
from flamapy.core.models import VariabilityModel

LOGGER = logging.getLogger('Metrics')


class Metrics(Operation):
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

    def only_these_metrics(self, filter_metrics: list[str]) -> None:
        self.filter = filter_metrics 

    def execute(self, model: VariabilityModel) -> 'Metrics':
        self.model = model
        # Identifying all implementations of MetricsOperation

        for subclass in Metrics.__subclasses__(): 
            # We first have to identify the metamodels that are being used and 
            # transform this model to the correspointing metamodel
            metrics_operation = subclass()

            if self.model.__class__.get_extension() == metrics_operation.model_type_extension:
                # If its the metamodel that math the model, calculate the metrics
                # Then we calculate the metrics for each metamodel
                self.result.append(subclass().calculate_metamodel_metrics(model))
            else:
                # If not, search a transformation, transform and call the calutation
                m_to_m = self._search_transformations(self.model.__class__.get_extension(), 
                                                      metrics_operation.model_type_extension)
                dest_model = m_to_m(self.model).transform()
                self.result.append(subclass().calculate_metamodel_metrics(dest_model))
        return self

    def _search_transformations(self, orig: str, dest: str) -> ModelToModel:
        try:
            for m_to_m in ModelToModel.__subclasses__():
                _orig = m_to_m.get_source_extension()
                _dest = m_to_m.get_destination_extension()
                if (_orig == orig and _dest == dest):
                    return m_to_m
        except FlamaException:
            LOGGER.exception("No transformation found that is required in the Metrics operation")
        raise FlamaException("No transformation found")

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
    def construct_result(name: Optional[str] = None,
                         doc: Optional[str] = None,
                         result: Optional[Any] = None, 
                         size: Optional[int] = None, 
                         ratio: Optional[float] = None
                         ) -> dict[str, Any]:
        """Constructs a dictionary with named keys from the provided list and other arguments.

            property name: The property name.
            description: The description of the property
            value (optional): the list of abstract features.
            size (optional): the length of the list.
            ratio (optional): the percentage of abstract features with regards the total number 
                              of features.
        """

        return {
            "name": name or "Default Name",  # Using a default value if name is None
            "documentation": doc or "Default Documentation",
            "result": result or [],
            "size": size or 0,
            "ratio": ratio or 0.0
        }
