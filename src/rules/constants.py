from typing import Any, List, Type

from deap.gp import PrimitiveSetTyped
from pandas.core.frame import DataFrame

from .base_rule import BaseRule
from .cossover import MACDRule
from .ema import EMARule
from .filter import FilterRule
from .operators import CommonOperators
from .ret_types import Signals
from .rsi import RSIRule
from .slope import SlopeRule

# from .price import PriceRule

RULES: List[Type[BaseRule]] = [CommonOperators, EMARule, FilterRule, RSIRule, SlopeRule, MACDRule]
TERMINALS: List[Any] = list(set([DataFrame, *sum((rule.get_terminals() for rule in RULES), [])]))
PSET = PrimitiveSetTyped("MAIN", [DataFrame], Signals)
PSET.renameArguments(ARG0="ohlcv")
for rule in RULES:
    try:
        rule.add_constants(PSET)
    except Exception as e:
        print(e)
    rule.add_primitives(PSET)
