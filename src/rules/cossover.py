import random
from typing import Any, Callable, ClassVar, Dict, List, Type

import pandas_ta as ta
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from .base_rule import BaseRule, BaseTerminal, Offset
from .ret_types import ComparableSeries, NotAbleSeries


class MACDFast(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class MACDSlow(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class MACDSignal(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class MACDRule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [MACDFast, MACDSlow, MACDSignal, Offset]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": crossover, "inputs": [ComparableSeries, ComparableSeries], "output":NotAbleSeries},
                {"func": macd_crossover, "inputs": [DataFrame, "MACDFast", "MACDSlow", "MACDSignal", "Offset"], "output":NotAbleSeries}]


def crossover(u: Series, v: Series):
    neg = u.le(v)
    pos = u.gt(v)
    return pos.shift(1) & neg


def macd_crossover(df: DataFrame, macd_fast: int, macd_slow: int, macd_signal: int, macd_offset: int):
    if macd_fast > macd_slow:
        macd_fast, macd_slow = macd_slow, macd_fast
    elif macd_fast == macd_slow:
        macd_slow += 1
    macd_full: DataFrame = df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, offset=macd_offset)
    macdh = macd_full.iloc[:, 1]
    zeros = Series(0, index=len(macdh))
    return crossover(macdh, zeros)
