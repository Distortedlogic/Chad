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

from old_src import CXPB, DEBUG, EXPR_MAX, EXPR_MIN, MAX_IND_SIZE, MUTPB
from old_src.api import decorators
from old_src.api.graphing import graph
from old_src.model.individual import Individual


@dataclass
class ToolBox:
    evaluate: Callable[[Individual], Tuple[Union[int, float], ...]]
    terminal_types: List[Any]
    pset: PrimitiveSetTyped

    def generate_expression(self,
                            pset: Optional[PrimitiveSetTyped] = None,
                            type_: Optional[type] = None,
                            min_: int = EXPR_MIN,
                            max_: int = EXPR_MAX):
        pset = pset or self.pset
        type_ = type_ or cast(type, pset.ret)
        expr: List[Any] = []
        height = randint(min_, max_)
        stack: List[Tuple[int, type]] = [(0, type_)]
        terminals_dict = cast(DefaultDict[type, List[Terminal]], pset.terminals)
        primitives_dict = cast(DefaultDict[type, List[Primitive]], pset.primitives)
        terminal_names = [terminal.__name__ for terminal in self.terminal_types]
        while len(stack) != 0:
            depth, type_ = stack.pop()
            if type_.__name__ in terminal_names:
                try:
                    terminal = choice(terminals_dict[type_])
                except IndexError:
                    graph(gp.PrimitiveTree(expr))
                    print(terminals_dict)
                    print(terminals_dict[type_])
                    print(type_)
                    _, _, traceback = exc_info()
                    raise IndexError("The gp.generate function tried to add "
                                     + "a inalinal of type '%s', but there is "
                                     + "none available.").with_traceback(traceback)
                if isclass(terminal):
                    terminal = terminal()
                expr.append(terminal)
            else:
                without_terminal_args = [p for p in primitives_dict[type_] if
                                         all([arg not in self.terminal_types for arg in p.args])]
                with_only_terminal_args = [p for p in primitives_dict[type_] if
                                           all([arg in self.terminal_types for arg in p.args])]
                with_mixed_args = [p for p in primitives_dict[type_]
                                   if p not in without_terminal_args
                                   and p not in with_only_terminal_args]
                try:
                    # Might not be respected if there is a type without terminal args
                    if height <= depth or (depth >= min_ and random() < pset.terminalRatio):
                        if len(with_only_terminal_args + with_mixed_args) == 0:
                            prim = choice(without_terminal_args)
                        else:
                            prim = choice(with_only_terminal_args + with_mixed_args)
                    else:
                        if len(without_terminal_args + with_mixed_args) == 0:
                            prim = choice(with_only_terminal_args)
                        else:
                            prim = choice(without_terminal_args + with_mixed_args)
                except IndexError:
                    graph(gp.PrimitiveTree(expr))
                    print("self.terminal_types", self.terminal_types)
                    print("primitives_dict", primitives_dict)
                    print("without_terminal_args", without_terminal_args)
                    print("with_only_terminal_args", with_only_terminal_args)
                    print("with_mixed_args", with_mixed_args)
                    print(type_)
                    print("type_ in self.terminal_types", type_ in self.terminal_types)
                    _, _, traceback = exc_info()
                    raise IndexError("The gp.generate function tried to add "
                                     + "a primitive of type '%s', but there is "
                                     + "none available." % (type_,)).with_traceback(traceback)
                expr.append(prim)
                for arg in reversed(prim.args):
                    stack.append((depth + 1, arg))

        # graph(gp.PrimitiveTree(expr))
        return expr

    def create_individual(self):
        return Individual(self.generate_expression())

    def create_population(self, size: int):
        return [self.create_individual() for _ in range(size)]

    def evaluate_pop(self, pop: List[Individual]):
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        if DEBUG:
            fitnesses = map(self.evaluate, invalid_ind)
        else:
            fitnesses = multiprocessing.Pool().map(self.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        return len(invalid_ind)

    def standard_step(self, pop: List[Individual]):
        offspring = [deepcopy(ind) for ind in pop]
        for i in range(1, len(offspring), 2):
            if random() < CXPB:
                if DEBUG:
                    print("mating offspring")
                offspring[i - 1], offspring[i] = self.mate(offspring[i - 1], offspring[i])
                del offspring[i - 1].fitness.values, offspring[i].fitness.values
        for i in range(len(offspring)):
            if random() < MUTPB:
                # if random() < 0.3:
                #     if DEBUG:
                #         print("mutating insert")
                #     (offspring[i],) = mutInsert(offspring[i], self.pset)
                if random() < 0.3:
                    if DEBUG:
                        print("mutating ephemeral rand")
                    (offspring[i],) = self.mutEphemeral_rand(offspring[i])
                elif random() < 0.3:
                    if DEBUG:
                        print("mutating node replacement")
                    (offspring[i],) = self.mutNodeReplacement(offspring[i])
                else:
                    if DEBUG:
                        print("mutating uniform")
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
    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
    def mate(cls, individual_1: Individual, individual_2: Individual, termpb: float = 0.1) -> Tuple[Individual, Individual]:
        return cxOnePointLeafBiased(individual_1, individual_2, termpb=termpb)

    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
    def mutate_uniform(self, individual: Individual) -> Tuple[Individual, ...]:
        return mutUniform(individual, self.generate_expression, pset=self.pset)

    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
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
    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
    def mutEphemeral(cls, individual: Individual, mode: str = "all") -> Tuple[Individual, ...]:
        return mutEphemeral(individual, mode="all")

    @classmethod
    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
    def mutEphemeral_rand(cls, individual: Individual) -> Tuple[Individual, ...]:
        ephemerals_idx = [index for index, node in enumerate(individual) if isinstance(node, Ephemeral)]
        if len(ephemerals_idx) > 0:
            ephemerals_idx = sample(ephemerals_idx, randint(1, len(ephemerals_idx)))
            for i in ephemerals_idx:
                individual[i] = type(individual[i])()

        return (individual,)

    @decorators.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE)
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
