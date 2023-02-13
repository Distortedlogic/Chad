from pathlib import Path
from typing import Any, List, cast

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from deap import gp
from IPython.core.display import display
from networkx.drawing.nx_agraph import graphviz_layout
from pandas._config.config import option_context
from pandas.core.frame import DataFrame
from pandas.core.series import Series

# from src import bta


def get_ohlcv_path(sym: str):
    path = f"src/data/ohlcv/"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path + f"{sym}.csv"


def load_ohlcv_df(sym: str, base: str, tf: str = "hour", limit: int = 20_000) -> DataFrame:
    path = get_ohlcv_path(sym)
    if Path(path).is_file():
        return pd.read_csv(path)
    # else:
    #     bta.update(sym, base, tf, limit)
    #     _ = bta.df.to_csv(path, index=False)
    #     return bta.df


def calc_sqn(history: DataFrame) -> float:
    trade_num = len(history)
    revenue = history["revenue"]
    q: float = revenue.quantile(0.95)
    history = history[revenue < q]
    mean_profit: float = revenue.mean()
    std_profit = revenue.std()
    root_num_trades = trade_num ** 0.5
    amplifier = (root_num_trades / std_profit
                 if mean_profit < 0
                 else std_profit / root_num_trades)
    return amplifier * mean_profit


def display_df(df: DataFrame):
    with option_context("display.max_rows", None, "display.max_columns", None):  # type:ignore
        _ = display(df)
