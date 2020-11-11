from famapy.core.discover import DiscoverMetamodels


# create the manager
dm = DiscoverMetamodels()

# Example t2m
fm = dm.use_transformation_t2m(src='example.xml', dst='fm')
print(fm)

# Example m2t
dm.use_transformation_m2t(src=fm, dst='output.json')


# Example m2m
# TODO: create VariabilityModel and get src extension
# todo debe haber alguna forma de pasarle el modelo cargado a la transformacion
# y que te lo devuelva en pysast
# dm.use_transformation_m2m(src=VariabilityModel, dst='pysat')
pysatm = dm.use_transformation_m2m(src=fm, dst='pysat')
print(pysatm)

# operation execute return the object instance
operation = dm.use_operation(src=pysatm, operation='Valid')
print("Result operation valid:", operation.is_valid())
