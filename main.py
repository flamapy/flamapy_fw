from famapy.metamodels.fm_metamodel.transformations.json_writter import JsonWriter
from famapy.metamodels.fm_metamodel.transformations.xml_transformation import XMLTransformation

from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid import Glucose3Valid
from famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat


# Parse a file
xmlreader = XMLTransformation("/mnt/c/Users/jagal/Documents/Repositories/FaMaPy/core/test.fama")
fm=xmlreader.transform()

#print the model
print(fm)

# Create a detination metamodel (Pysat for the record)
sat= PySATModel()

# Transform the first onto the second
transform = FmToPysat(fm, sat)
transform.transform()

# Create the operation
valid = Glucose3Valid()

# Execute the operation . TODO Investigate how t avoid that sat parameter
valid.execute(sat)

# Print the result
print("Is the model valid: " + str(valid.isValid()))

# Create the operation
products = Glucose3Products()

# Execute the operation . TODO Investigate how t avoid that sat parameter
products.execute(sat)

# Print the result
print("The products encoded in the model are: ")
print(products.getProducts())

# Save the model as json

w = JsonWriter("./data.json", fm)
w.transform()
