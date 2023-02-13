import random
from typing import Any, Callable, ClassVar, Dict, List, Type

import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from old_src.rules.ret_types import (BoolSeries, ComparableSeries,
                                     FilterableSeries, NotAbleSeries, Signals)

from .base_rule import BaseRule, BaseTerminal


class MinHold(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 100}]


class CommonOperators(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [MinHold]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": combine_signals, "inputs": [BoolSeries, BoolSeries, DataFrame, "MinHold"], "output":Signals},
                {"func": and_, "inputs": [BoolSeries, BoolSeries], "output":NotAbleSeries},
                {"func": or_, "inputs": [BoolSeries, BoolSeries], "output":NotAbleSeries},
                {"func": not_, "inputs": [BoolSeries], "output":BoolSeries},
                {"func": compare, "inputs": [ComparableSeries, ComparableSeries], "output":FilterableSeries}]


def combine_signals(u: Series, v: Series, df: DataFrame, min_hold: int):
    signal = pd.concat([u.rename("buy"), v.rename("sell")], axis=1)
    not_buy_and_sell: Series = ~(signal["buy"] & signal["sell"]).astype(bool)
    signal = signal.where(not_buy_and_sell, other=0)
    signal = pd.concat([signal, df["close"]], axis=1)
    signal: DataFrame = signal[250:].reset_index(drop=True)
    signal = signal[(signal["buy"] == True) | (signal["sell"] == True)]
    return signal, min_hold


def and_(u: Series, v: Series):
    return u & v


def or_(u: Series, v: Series):
    return u | v


def not_(u: Series) -> Series:
    return ~u


def compare(u: Series, v: Series):
    return u.lt(v)
