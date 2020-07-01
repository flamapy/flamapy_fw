import time

from pysat.formula import CNF
from pysat.solvers import Glucose3

from core.models.VariabilityModel import VariabilityModel
from core.transformations.ModelToModel import ModelToModelTransformation
from fm_metamodel.model.FeatureModel import Feature, FeatureModel, Relation


class SAT(VariabilityModel):

    def __init__(self):
        self.cnf = CNF()

    def add_constraint(self, constraint):
        cnf.append(constraint)

    def is_valid(self) -> bool:
        g = Glucose3()
        for clause in self.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint
        starttime = time.time()
        sol = g.solve()
        reqtime = time.time() - starttime
        return sol

    def products(self):  # TODO
        return None


class Test2SAT(ModelToModelTransformation):
    def __init__(self, model1: VariabilityModel, model2: VariabilityModel):
        self.counter = 1
        self.variables = {}
        self.model1 = model1
        self.model2 = model2
        self.cnf = model2.cnf

    def add_feature(self, feature):
        if not feature.name in self.variables.keys():
            self.variables[feature.name] = self.counter
            self.counter += 1

    def add_relation(self, relation):
        self.cnf.append([-1 * self.variables.get(relation.parent.name),
                    self.variables.get(relation.children[0].name)])

    def transform(self):
        for feature in self.model1.get_features():
            self.add_feature(feature)
        for relation in self.model1.get_relations():
            self.add_relation(relation)


# SAT
sat = SAT()

# Test
feature_b = Feature('B', [])
relation = Relation(parent=None, children=[feature_b], card_min=0, card_max=1)
feature_a = Feature('A', [relation])
relation.parent = feature_a
fm = FeatureModel(feature_a, [])

print(fm)

transform = Test2SAT(fm, sat)
transform.transform()
print(sat.is_valid())
