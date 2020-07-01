from core.models.VariabilityModel import VariabilityModel
from core.transformations.ModelToModel import ModelToModelTransformation
from fm_metamodel.model.FeatureModel import Feature, FeatureModel, Relation
from pysat_metamodel.model.PySATModel import PySATModel
from pysat_metamodel.transformations.fm_to_pysat import Fm_to_pysat
from pysat_metamodel.operations.Glucose3Valid import Glucose3Valid
from pysat_metamodel.operations.Glucose3Products import Glucose3Products

# Create a small fm manually //readers yet missing
feature_b = Feature('B', [])
relation = Relation(parent=None, children=[feature_b], card_min=0, card_max=1)
feature_a = Feature('A', [relation])
relation.parent = feature_a
fm = FeatureModel(feature_a, [])

# Create a detination metamodel (Pysat for the record)
sat= PySATModel()

# Transform the first onto the second
transform = Fm_to_pysat(fm, sat)
transform.transform()

# Create the operation
valid = Glucose3Valid()

# Execute the operation . TODO Investigate how t avoid that sat parameter
valid.execute(sat)

# Print the result
print(valid.isValid())

# Create the operation
products = Glucose3Products()

# Execute the operation . TODO Investigate how t avoid that sat parameter
products.execute(sat)

# Print the result
print(products.getProducts())
