from typing import Any, Tuple, cast

from deap import gp
from deap.gp import PrimitiveSetTyped
from pandas.core.frame import DataFrame

from src.deap_utils.individual import Individual
from src.Settings import TradeSettings
from src.TradeHistory import ETradeSide, TradeHistory


def fitness(individual: Individual,
            *,
            df: DataFrame,
            pset: PrimitiveSetTyped):
    position = 0
    history = TradeHistory()
    signals, _ = cast(Tuple[DataFrame, int], gp.compile(individual, pset)(df))
    for time_index, row in cast(list[tuple[int, dict[str, Any]]], signals.iterrows()):
        if row["buy"] and row["sell"]:
            continue
        if row["buy"] and position < TradeSettings.POSITION_BOUND:
            position += TradeSettings.MAX_TRADE_AMOUNT
            side = ETradeSide.Buy
        elif row["sell"] and position > -TradeSettings.POSITION_BOUND:
            position -= TradeSettings.MAX_TRADE_AMOUNT
            side = ETradeSide.Sell
        else:
            continue
        amount = row["close"] * TradeSettings.MAX_TRADE_AMOUNT
        history.update_history(side, time_index, amount)
    return history.get_score()
