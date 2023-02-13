import random
from typing import Any, Callable, ClassVar, Dict, List, Type, cast

import pandas_ta as ta
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from old_src.rules.ret_types import FilterableSeries

from .base_rule import BaseRule, BaseTerminal, Offset


class RSILength(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class RSIDrift(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 10}]


class RSILower(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 10, "upper": 40}]


class RSIUpper(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 60, "upper": 90}]


class RSIRule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [RSILength, RSIDrift, Offset, RSILower, RSIUpper]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": rsi_lt, "inputs": [DataFrame, "RSILength", "RSIDrift", "Offset", "RSILower"], "output":FilterableSeries},
                {"func": rsi_gt, "inputs": [DataFrame, "RSILength", "RSIDrift", "Offset", "RSIUpper"], "output":FilterableSeries}]


def rsi_(df: DataFrame, length: int, drift: int, offset: int):
    return cast(Series, df.ta.rsi(length=length, drift=drift, offset=offset))


def rsi_lt(df: DataFrame, length: int, drift: int, offset: int, threshold: float):
    return rsi_(df, length=length, drift=drift, offset=offset) < threshold


def rsi_gt(df: DataFrame, length: int, drift: int, offset: int, threshold: float):
    return rsi_(df, length=length, drift=drift, offset=offset) > threshold
