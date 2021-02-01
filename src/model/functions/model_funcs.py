import pickle
import random
from pathlib import Path

from deap import tools
from src import HOF_SIZE, POP_SIZE, RND_SEED_INT, VERSION
from src.model.functions.population import evaluate_pop


def init_cp(toolbox, stats):
    random.seed(RND_SEED_INT)
    pop = toolbox.population(n=POP_SIZE)
    evaluate_pop(toolbox, pop)
    hall_of_fame = tools.HallOfFame(HOF_SIZE)
    hall_of_fame.update(pop)
    logbook = tools.Logbook()
    logbook.header = ["gen"] + (stats.fields)
    return dict(
        pop_size=POP_SIZE,
        version=VERSION,
        generation=0,
        pop=pop,
        logbook=logbook,
        hall_of_fame=hall_of_fame,
        rndstate=random.getstate(),
    )


def load_cp(toolbox, stats, fresh):

    if fresh:
        path = get_path("init")
        if Path(path).is_file():
            with open(get_path("init"), "rb") as save_file:
                cp = pickle.load(save_file)
        else:
            cp = init_cp(toolbox, stats)
            checkpoint_cp(cp, True)
    else:
        path = get_path("trained")
        if Path(path).is_file():
            with open(path, "rb") as save_file:
                cp = pickle.load(save_file)
        else:
            cp = init_cp(toolbox, stats)
            checkpoint_cp(cp, True)
    random.setstate(cp["rndstate"])
    return cp


def checkpoint_cp(cp, init=False):
    with open(get_path("init" if init else "trained"), "wb") as save_file:
        pickle.dump(cp, save_file)


def get_path(name):
    path = f"src/data/{VERSION}/{POP_SIZE}/"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path + f"{name}.pkl"
