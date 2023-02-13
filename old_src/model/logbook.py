import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List, cast

import numpy as np
import pandas
from arrow.api import now
from IPython.core.display import clear_output
from pandas.core.frame import DataFrame

from old_src import DEBUG
from old_src.api.dataframe import display_df
from old_src.api.time_utils import secondsToText
from old_src.model.checkpoint import Checkpoint
from old_src.model.individual import Individual


def init_df():
    return DataFrame(columns=["distinct",
                              "num_changed",
                              "min_height",
                              "avg_height",
                              "max_height",
                              "best_height",
                              "mean",
                              "max",
                              "std",
                              "run_time"])


@dataclass
class Logbook:
    folder: ClassVar[str] = "src/data/logbooks/"
    uuid: str
    df: DataFrame = field(default_factory=init_df)

    def log(self, checkpoint: Checkpoint):
        best: Individual = checkpoint.hall_of_fame[0]
        distinct = len(set(individual.__hash__() for individual in checkpoint.population))
        heights = list(individual.height for individual in checkpoint.population)
        min_height = int(np.amin(heights))
        avg_height = int(np.mean(list(heights)))
        max_height = int(np.amax(list(heights)))
        best_height: int = best.height
        run_time = now()-checkpoint.now
        checkpoint.now = now()
        self.df = self.df.append(dict(distinct=distinct,
                                      num_changed=checkpoint.num_changed,
                                      min_height=min_height,
                                      avg_height=avg_height,
                                      max_height=max_height,
                                      best_height=best_height,
                                      mean=int(self.mean(checkpoint.population)),
                                      max=int(best.fitness.values[0]),
                                      std=int(self.std(checkpoint.population)),
                                      run_time=secondsToText(int(run_time.total_seconds()))),
                                 ignore_index=True)

    def display(self, clear: bool = False):
        if clear:
            clear_output()
            display_df(self.df.iloc[-5:])
        else:
            display_df(self.df.iloc[-1:])

    @classmethod
    def get_path(cls, uuid: str):
        Path(cls.folder).mkdir(parents=True, exist_ok=True)
        return cls.folder + f"{uuid}.pkl"

    def save(self):
        if not DEBUG:
            self.df.to_pickle(self.get_path(self.uuid))

    @classmethod
    def load(cls, uuid: str):
        if Path(cls.get_path(uuid)).is_file():
            df: DataFrame = pandas.read_pickle(cls.get_path(uuid))
            return Logbook(uuid, df)
        return Logbook(uuid)

    def clear_book(self, uuid: str):
        self.df = init_df()
        if Path(self.get_path(uuid)).is_file():
            shutil.rmtree(self.folder)

    @classmethod
    def clear(cls, uuid: str):
        if Path(cls.get_path(uuid)).is_file():
            shutil.rmtree(cls.folder)

    @staticmethod
    def get_fitness_values(individual: Individual):
        return cast(float, individual.fitness.values[0])

    @classmethod
    def get_values(cls, individuals: List[Individual]):
        return list(cls.get_fitness_values(individual) for individual in individuals)

    @classmethod
    def mean(cls, individuals: List[Individual]):
        return cast(float, np.mean(cls.get_values(individuals)))

    @classmethod
    def max(cls, individuals: List[Individual]):
        return cast(float, np.amax(cls.get_values(individuals)))

    @classmethod
    def std(cls, individuals: List[Individual]):
        values = cls.get_values(individuals)
        # set_values = set(values)
        # if len(set_values) == 1 and list(set_values)[0] != -99999:
        #     print("values", values)
        #     raise ValueError("std all the same")
        return cast(float, np.std(values))
