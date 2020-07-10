from core.models.VariabilityModel import VariabilityModel
from core.transformations.ModelToModel import ModelToModel
from fm_metamodel.model.FeatureModel import Feature, FeatureModel, Relation
from fm_metamodel.transformations.XMLTransformation import XMLTransformation
from fm_metamodel.transformations.JsonWritter import JsonWriter

from pysat_metamodel.model.PySATModel import PySATModel
from pysat_metamodel.transformations.fm_to_pysat import Fm_to_pysat
from pysat_metamodel.operations.Glucose3Valid import Glucose3Valid
from pysat_metamodel.operations.Glucose3Products import Glucose3Products

# Parse a file
xmlreader = XMLTransformation("/mnt/c/Users/jagal/Documents/Repositories/FaMaPy/core/test.fama")
fm=xmlreader.transform()

#print the model
print(fm)

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
print("Is the model valid: "+ str(valid.isValid()))

# Create the operation
products = Glucose3Products()

# Execute the operation . TODO Investigate how t avoid that sat parameter
products.execute(sat)

# Print the result
print("The products encoded in the model are: ")
print(products.getProducts())

# Save the model as json

w=JsonWriter("./data.json",fm)
w.transform()