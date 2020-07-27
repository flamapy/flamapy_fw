from famapy.core.discover import DiscoverMetamodels


dm = DiscoverMetamodels()

# Example m2t
from famapy.metamodels.fm_metamodel.models.FeatureModel import FeatureModel
# TODO: create FeatureModel
fm = FeatureModel(root=None, constraint=[])
dm.use_transformation_m2t(src=fm, dst='/tmp/output.json')


# Example t2m
dm.use_transformation_t2m(src='/tmp/in.xml', dst=FeatureModel)


# Example m2m
# TODO: create VariabilityModel and get src extension
dm.use_transformation_m2m(src=VariabilityModel, dst='pysat')


from famapy.core.operations.Valid import Valid
from famapy.metamodels.pysat_metamodel.models import PySATModel
# TODO: create pysat_model
pysat_model = PySATModel()
dm.use_operation(src=pysat_model, op=Valid)
