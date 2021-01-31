import multiprocessing
import operator
import random

from deap import algorithms, base, creator, gp, tools
from deap.gp import Ephemeral
from src import MAX_IND_SIZE
from src.model.functions.build_pset import build_pset
from src.model.utils.mutInsert import mutInsert
from src.model.utils.mutNodeReplacement import mutNodeReplacement
from src.model.utils.safe_gen import generate_safe


def mutEphemeral_rand(individual):
    ephemerals_idx = [
        index for index, node in enumerate(individual) if isinstance(node, Ephemeral)
    ]
    if len(ephemerals_idx) > 0:
        ephemerals_idx = random.sample(
            ephemerals_idx, random.randint(1, len(ephemerals_idx))
        )
        for i in ephemerals_idx:
            individual[i] = type(individual[i])()

    return (individual,)


def fitness_gt(pop, limit):
    chosen = []
    for i in range(len(pop)):
        if pop[i].fitness.values[0] > limit:
            chosen.append(pop[i])
    return chosen


def load_toolbox():
    pset, terminal_types = build_pset()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create(
        "Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=pset
    )

    toolbox = base.Toolbox()
    toolbox.register("map", multiprocessing.Pool().map)
    toolbox.register("imap", multiprocessing.Pool().imap)
    toolbox.register(
        "expr",
        generate_safe,
        pset=pset,
        min_=5,
        max_=10,
        terminal_types=terminal_types,
    )
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    toolbox.register("selTournament", tools.selTournament)
    toolbox.register(
        "selDoubleTournament",
        tools.selDoubleTournament,
        parsimony_size=1.4,
        fitness_first=True,
    )
    toolbox.register("selBest", tools.selBest)
    toolbox.register("fitness_gt", fitness_gt)
    toolbox.register("mate", gp.cxOnePointLeafBiased, termpb=0.1)
    toolbox.register("mutUniform", gp.mutUniform, expr=toolbox.expr, pset=pset)
    toolbox.register("mutNodeReplacement", mutNodeReplacement, pset=pset)
    toolbox.register("mutEphemeral", gp.mutEphemeral, mode="all")
    toolbox.register("mutEphemeral_rand", mutEphemeral_rand)
    toolbox.register("mutInsert", mutInsert)
    toolbox.register("mutShrink", gp.mutShrink)

    toolbox.decorate(
        "mate",
        gp.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE),
    )
    toolbox.decorate(
        "mutUniform",
        gp.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE),
    )
    toolbox.decorate(
        "mutNodeReplacement",
        gp.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE),
    )
    toolbox.decorate(
        "mutEphemeral",
        gp.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE),
    )
    toolbox.decorate(
        "mutEphemeral_rand",
        gp.staticLimit(key=operator.attrgetter("height"), max_value=MAX_IND_SIZE),
    )
    return pset, toolbox
