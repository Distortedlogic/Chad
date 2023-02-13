import random
from typing import Any, Callable, ClassVar, Dict, List, Type, cast

import pandas_ta as ta
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from .base_rule import BaseRule, BaseTerminal, Offset
from .ret_types import ComparableSeries, FilterableSeries


class DiffLower(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": -1, "upper": 0}]


class DiffUpper(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 1}]


class PriceRule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [DiffLower, DiffUpper, Offset]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": price, "inputs": [DataFrame], "output":ComparableSeries},
                {"func": _vwap, "inputs": [DataFrame, "Offset"], "output":ComparableSeries},
                {"func": percent_diff_lt, "inputs": [DataFrame, "DiffUpper"], "output":FilterableSeries},
                {"func": percent_diff_gt, "inputs": [DataFrame, "DiffUpper"], "output":FilterableSeries},
                {"func": percent_diff_vwap_lt, "inputs": [DataFrame, "Offset", "DiffUpper"], "output":FilterableSeries},
                {"func": percent_diff_vwap_gt, "inputs": [DataFrame, "Offset", "DiffUpper"], "output":FilterableSeries}]


def price(u: DataFrame):
    return u['close']


def _vwap(u: DataFrame, vwap_offset: int) -> Series:
    return cast(Series, u.ta.vwap(offset=vwap_offset))


def percent_diff_vwap_lt(u: DataFrame, vwap_offset: int, diff_lower: float):
    close = u['close']
    vwap_series = _vwap(u, vwap_offset)
    sub = cast(Series, close.sub(vwap_series))
    return sub.divide(close) < diff_lower


def percent_diff_vwap_gt(u: DataFrame, vwap_offset: int, diff_upper: float):
    close = u['close']
    vwap_series = _vwap(u, vwap_offset)
    sub = cast(Series, close.sub(vwap_series))
    return sub.divide(close) > diff_upper


def percent_diff_lt(u: DataFrame, diff_lower: float):
    return u['close'].pct_change() < diff_lower


def percent_diff_gt(u: DataFrame, diff_upper: float):
    return u['close'].pct_change() > diff_upper
