import hashlib
from typing import Any

from deap import base
from deap.gp import PrimitiveTree


class FitnessMax(base.Fitness):
    weights = (1.0,)


class Individual(PrimitiveTree):
    def __init__(self, content: Any):
        PrimitiveTree.__init__(self, content)
        self.fitness = FitnessMax()

    def __eq__(self, other: "Individual"):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return int(hashlib.sha256(self.__str__().encode("utf-8")).hexdigest(), 16)
