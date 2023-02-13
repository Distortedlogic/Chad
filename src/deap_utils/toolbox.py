import multiprocessing
import operator
from copy import deepcopy
from dataclasses import dataclass
from inspect import isclass
from random import choice, randint, random, randrange, sample, shuffle
from sys import exc_info
from typing import (Any, Callable, DefaultDict, List, Optional, Tuple, Union,
                    cast)

from deap import gp, tools
from deap.gp import (Ephemeral, Primitive, PrimitiveSetTyped, Terminal,
                     cxOnePointLeafBiased, mutEphemeral, mutShrink, mutUniform)
from pandas.core.frame import DataFrame

from deap_utils import staticLimit
from src.deap_utils.fitness import fitness
from src.deap_utils.generate_expression import generate_expression
from src.deap_utils.individual import Individual
from src.Settings import DeapSettings, TrainingSettings


@dataclass
class ToolBox:
    terminal_types: List[Any]
    pset: PrimitiveSetTyped

    def create_individual(self):
        return Individual(generate_expression())

    def create_population(self, size: int):
        return [self.create_individual() for _ in range(size)]

    def evaluate_pop(self, pop: List[Individual]):
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        if TrainingSettings.DEBUG:
            fitnesses = map(fitness, invalid_ind)
        else:
            fitnesses = multiprocessing.Pool().map(fitness, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        return len(invalid_ind)

    def standard_step(self, pop: List[Individual]):
        offspring = [deepcopy(ind) for ind in pop]
        for i in range(1, len(offspring), 2):
            if random() < DeapSettings.CXPB:
                offspring[i - 1], offspring[i] = self.mate(offspring[i - 1], offspring[i])
                del offspring[i - 1].fitness.values, offspring[i].fitness.values
        for i in range(len(offspring)):
            if random() < DeapSettings.MUTPB:
                # if random() < 0.3:
                #     if DEBUG:
                #         print("mutating insert")
                #     (offspring[i],) = mutInsert(offspring[i], self.pset)
                if random() < 0.3:
                    (offspring[i],) = self.mutEphemeral_rand(offspring[i])
                elif random() < 0.3:
                    (offspring[i],) = self.mutNodeReplacement(offspring[i])
                else:
                    (offspring[i],) = self.mutate_uniform(offspring[i])
                del offspring[i].fitness.values
        num_changed = self.evaluate_pop(offspring)
        return offspring, num_changed

    def tree_to_function(self, individual: Individual) -> Callable[[DataFrame], DataFrame]:
        return gp.compile(individual, pset=self.pset)

    @classmethod
    def select_best(cls, individuals: List[Individual], size: int) -> List[Individual]:
        return tools.selBest(individuals, size)

    @classmethod
    def selTournament(cls, individuals: List[Individual], size: int, tournament_size: int) -> List[Individual]:
        return tools.selTournament(individuals, size, tournament_size)

    @classmethod
    def selDoubleTournament(cls, individuals: List[Individual], size: int, fitness_size: int) -> List[Individual]:
        return tools.selDoubleTournament(individuals, size, fitness_size, parsimony_size=1.4, fitness_first=True,)

    @classmethod
    def fitness_greater_than(cls, pop: List[Individual], limit: float):
        chosen: List[Any] = []
        for i in range(len(pop)):
            if pop[i].fitness.values[0] > limit:
                chosen.append(pop[i])
        return chosen

    @classmethod
    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mate(cls, individual_1: Individual, individual_2: Individual, termpb: float = 0.1) -> Tuple[Individual, Individual]:
        return cxOnePointLeafBiased(individual_1, individual_2, termpb=termpb)

    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mutate_uniform(self, individual: Individual) -> Tuple[Individual, ...]:
        return mutUniform(individual, generate_expression, pset=self.pset)

    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mutNodeReplacement(self, individual: Individual) -> Tuple[Individual, ...]:
        if len(individual) < 2:
            return individual,

        found = False
        prim_indices = [idx for idx, node in enumerate(individual) if node.arity != 0]
        while not found and prim_indices:
            shuffle(prim_indices)
            index = prim_indices.pop()
            node = individual[index]

            prims = [p for p in self.pset.primitives[node.ret] if p.args == node.args and type(p) != type(node)]
            if len(prims) > 1:
                individual[index] = choice(prims)
                found = True

        return individual,

    @classmethod
    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mutEphemeral(cls, individual: Individual, mode: str = "all") -> Tuple[Individual, ...]:
        return mutEphemeral(individual, mode="all")

    @classmethod
    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mutEphemeral_rand(cls, individual: Individual) -> Tuple[Individual, ...]:
        ephemerals_idx = [index for index, node in enumerate(individual) if isinstance(node, Ephemeral)]
        if len(ephemerals_idx) > 0:
            ephemerals_idx = sample(ephemerals_idx, randint(1, len(ephemerals_idx)))
            for i in ephemerals_idx:
                individual[i] = type(individual[i])()

        return (individual,)

    @staticLimit.staticLimit(key=operator.attrgetter("height"), max_value=DeapSettings.MAX_IND_SIZE)
    def mutate_insert(self, individual: Individual) -> Tuple[Individual, ...]:
        index = randrange(len(individual))
        node = individual[index]
        slice_ = individual.searchSubtree(index)
        # As we want to keep the current node as children of the new one,
        # it must accept the return value of the current node
        primitives = [p for p in self.pset.primitives[node.ret] if node.ret in p.args]
        if len(primitives) == 0:
            return individual,
        new_node = choice(primitives)
        new_subtree = [None] * len(new_node.args)
        position = choice([i for i, a in enumerate(new_node.args) if a == node.ret])
        new_nodes: List[Any] = [new_node]
        while new_nodes:
            new_node = new_nodes.pop()
            for i, arg_type in enumerate(new_node.args):
                terminals = self.pset.terminals[arg_type]
                primivites = self.pset.primitives[arg_type]
                if i != position:
                    if terminals:
                        terminal = choice(terminals)
                        if isclass(terminal):
                            terminal = terminal()
                        new_subtree[i] = terminal
                    elif primivites:
                        new_primitive = choice(primivites)
                        new_subtree[i] = new_primitive
                        new_nodes.append(new_primitive)

        new_subtree[position:position + 1] = individual[slice_]
        new_subtree.insert(0, new_node)
        individual[slice_] = new_subtree
        return individual,

    @classmethod
    def mutate_shrink(cls, individual: Individual) -> Tuple[Individual, ...]:
        return mutShrink(individual)
