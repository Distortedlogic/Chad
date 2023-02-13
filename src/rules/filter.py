
import random
from typing import Any, Callable, ClassVar, Dict, List, Type

from pandas.core.series import Series
from src.rules.ret_types import FilterableSeries, NotAbleSeries

from .base_rule import BaseRule, BaseTerminal


class FilterInt(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 1}]


class FilterRule(BaseRule):
    @staticmethod
    def get_base_terminals() -> List[Type[BaseTerminal]]:
        return [FilterInt]

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        return [{"func": signal_filter, "inputs": [FilterableSeries, "FilterInt", "FilterInt"], "output":NotAbleSeries}]


def signal_filter(u: Series, filter_int_1: int, filter_int_2: int) -> Series:
    if filter_int_1 < filter_int_2:
        filter_window = filter_int_2
        filter_trigger = filter_int_1
    else:
        filter_window = filter_int_1
        filter_trigger = filter_int_2
    return u.rolling(filter_window).sum() >= filter_trigger
