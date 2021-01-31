import numpy as np
from deap import tools


def load_stats():
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    stats.register("std", np.std)
    return stats
