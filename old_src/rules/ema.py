import random
from typing import Any, Callable, ClassVar, Dict, List, Type, cast

import pandas_ta as ta
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from old_src.rules.ret_types import ComparableSeries, FilterableSeries

from .base_rule import BaseRule, BaseTerminal, Offset


class EMALength(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class EMALower(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": -1, "upper": 0}]


class EMAUpper(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 1}]


class EMARule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [EMALength, Offset, EMALower, EMAUpper]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": ema_, "inputs": [DataFrame, "EMALength", "Offset"], "output":ComparableSeries},
                {"func": ema_lt, "inputs": [DataFrame, "EMALength", "Offset", "EMALower"], "output":FilterableSeries},
                {"func": ema_gt, "inputs": [DataFrame, "EMALength", "Offset", "EMAUpper"], "output":FilterableSeries}]


def ema_(df: DataFrame, length: int, offset: int):
    return cast(Series, df.ta.ema(length=length, offset=offset))


def ema_diff(df: DataFrame, length: int, offset: int):
    prices = df["close"]
    ema_series = ema_(df, length=length, offset=offset)
    subtracted = cast(Series, prices.subtract(ema_series))
    return subtracted.divide(prices)


def ema_lt(df: DataFrame, length: int, offset: int, ema_lower: float):
    return ema_diff(df, length, offset) < ema_lower


def ema_gt(df: DataFrame, length: int, offset: int, ema_upper: float):
    return ema_diff(df, length, offset) > ema_upper
