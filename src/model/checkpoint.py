import pickle
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from random import getstate
from typing import Any, ClassVar, Dict, List
from uuid import uuid4

from arrow import now
from deap.tools.support import HallOfFame
from src import (DEBUG, HOF_SIZE, LIMIT, MAX_TRADE_AMOUNT, MIN_NUM_TRADES,
                 PAIRS, POP_SIZE, POSITION_BOUND, RND_SEED_INT, TIMEFRAME,
                 VERSION)
from src.model.individual import Individual
from src.model.toolbox import ToolBox
from src.rules.constants import PSET, TERMINALS


@dataclass
class Checkpoint:
    folder: ClassVar[str] = f"src/data/{VERSION}/{POP_SIZE}/"
    uuid: str = field(default_factory=lambda: uuid4().hex)
    pop_size: int = POP_SIZE
    version: str = VERSION
    generation: int = 0
    toolbox_kwargs: Dict[str, Any] = field(default_factory=lambda: {"terminal_types": TERMINALS, "pset": PSET})
    population: List[Individual] = field(default_factory=lambda: ToolBox(terminal_types=TERMINALS, pset=PSET, evaluate=lambda x: (0,)).create_population(POP_SIZE))
    hall_of_fame: HallOfFame = field(default_factory=lambda: HallOfFame(HOF_SIZE))
    chad_kwargs: Dict[str, Any] = field(default_factory=lambda: {"pairs": PAIRS,
                                                                 "timeframe": TIMEFRAME,
                                                                 "limit": LIMIT,
                                                                 "position_bound": POSITION_BOUND,
                                                                 "max_trade_amount": MAX_TRADE_AMOUNT,
                                                                 "min_num_trades": MIN_NUM_TRADES,
                                                                 "pset": PSET})
    random_state: object = field(init=False)

    def __post_init__(self):
        random.seed(RND_SEED_INT)
        self.random_state = getstate()
        self.num_changed = 0
        self.now = now()

    @classmethod
    def get_path(cls, name: str):
        Path(cls.folder).mkdir(parents=True, exist_ok=True)
        return cls.folder + f"{name}.pkl"

    def checkpoint(self, init: bool = False):
        if not DEBUG:
            with open(self.get_path("init" if init else "trained"), "wb") as save_file:
                pickle.dump(self, save_file)

    @classmethod
    def clear(cls):
        if Path(cls.get_path("init")).is_file():
            shutil.rmtree(cls.folder)
        if Path(cls.get_path("trained")).is_file():
            shutil.rmtree(cls.folder)

    @classmethod
    def load(cls, fresh: bool):
        path = cls.get_path("init") if fresh else cls.get_path("trained")
        if Path(path).is_file():
            with open(path, "rb") as save_file:
                cp: Checkpoint = pickle.load(save_file)
            random.setstate(cp.random_state)
        else:
            cp: Checkpoint = cls()
            cp.checkpoint(True)
        return cp
