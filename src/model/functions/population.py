import random

from deap import tools
from src import CXPB, MUTPB, POP_SIZE


def evaluate_pop(toolbox, pop):
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit


def standard_step(toolbox, pop):
    offspring = [toolbox.clone(ind) for ind in pop]
    for i in range(1, len(offspring), 2):
        if random.random() < CXPB:
            offspring[i - 1], offspring[i] = toolbox.mate(
                offspring[i - 1], offspring[i]
            )
            del offspring[i - 1].fitness.values, offspring[i].fitness.values
    for i in range(len(offspring)):
        if random.random() < MUTPB:
            if random.random() < 0.3:
                (offspring[i],) = toolbox.mutEphemeral_rand(offspring[i])
            else:
                (offspring[i],) = toolbox.mutUniform(offspring[i])
            del offspring[i].fitness.values
    evaluate_pop(toolbox, offspring)
    return offspring
