from flamapy.core.discover import DiscoverMetamodels
dm = DiscoverMetamodels()

result = dm.get_plugins()

features = []
for r in result:
    features.append(r['name'])

print(result)