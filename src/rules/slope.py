import random
from typing import Any, Callable, ClassVar, Dict, List, Type, cast

import pandas_ta as ta
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from .base_rule import BaseRule, BaseTerminal, Offset
from .ret_types import FilterableSeries


class SlopeLength(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 1, "upper": 1000}]


class SlopeUpper(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 100}]


class SlopeLower(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.uniform
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": -100, "upper": 0}]


class SlopeRule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [SlopeLength, Offset, SlopeUpper, SlopeLower]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": slope_lt, "inputs": [DataFrame, "SlopeLength", "Offset", "SlopeLower"], "output":FilterableSeries},
                {"func": slope_gt, "inputs": [DataFrame, "SlopeLength", "Offset", "SlopeUpper"], "output":FilterableSeries}]


def slope_(df: DataFrame, slope_length: int, slope_offset: int):
    return cast(Series, df.ta.slope(slope_length, slope_offset))


def slope_gt(u: DataFrame, slope_length: int, slope_offset: int, slope_upper: float):
    return slope_(u, slope_length, slope_offset) > slope_upper


def slope_lt(u: DataFrame, slope_length: int, slope_offset: int, slope_lower: float):
    return slope_(u, slope_length, slope_offset) < slope_lower
