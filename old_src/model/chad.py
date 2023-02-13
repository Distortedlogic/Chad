from dataclasses import dataclass
from time import time
from typing import Any, Callable, Dict, List, Literal, Tuple, Union, cast

from deap import gp
from deap.gp import PrimitiveSetTyped
from pandas.core.frame import DataFrame

from old_src.api.dataframe import calc_sqn, display_df, load_ohlcv_df
from old_src.model.individual import Individual

TSide = Union[Literal["buy"], Literal["sell"]]


def opp_side(side: TSide):
    if side == "sell":
        return "buy"
    elif side == "buy":
        return "sell"
    raise Exception("bad side")


@dataclass
class Chad:
    pairs: List[Tuple[str, str]]
    timeframe: str
    limit: int
    position_bound: float
    max_trade_amount: float
    min_num_trades: int
    pset: PrimitiveSetTyped

    def __post_init__(self):
        self.dfs = [load_ohlcv_df(pair[0], pair[1], tf=self.timeframe, limit=self.limit)for pair in self.pairs]

    @property
    def close(self):
        close = self.dfs[0]["close"]
        for df in self.dfs[1:]:
            close = close.append(df["close"], ignore_index=True).reset_index(drop=True)
        return close

    @classmethod
    def get_default_history(cls):
        return DataFrame(columns=["entry",
                                  "exit",
                                  "type",
                                  "closed",
                                  "entry_time",
                                  "exit_time",
                                  "revenue"])

    def fitness(self, individual: Individual):
        now = time()
        self.individual = individual
        self.history = self.get_default_history()
        compiled: Callable[..., Tuple[DataFrame, int]] = gp.compile(individual, self.pset)
        position = 0
        for df in self.dfs:
            signals, _ = compiled(df)
            for time_index, row in cast(list[tuple[int, dict[str, Any]]], signals.iterrows()):
                if row["buy"] and row["sell"]:
                    continue
                if row["buy"] and position < self.position_bound:
                    position += self.max_trade_amount
                    side = "buy"
                elif row["sell"] and position > -self.position_bound:
                    position -= self.max_trade_amount
                    side = "sell"
                else:
                    continue
                close = cast(float, row["close"])
                amount = close * self.max_trade_amount
                self.update_history(side, time_index, amount)
            self.history = self.history[self.history["closed"] == True]
        self.runtime = time() - now
        if len(self.history) < self.min_num_trades or self.history["revenue"].std() == 0:
            return (-99999 + len(self.history),)
        return (calc_sqn(self.history),)

    def all_positions_closed(self, side: TSide) -> bool:
        type = "long" if opp_side(side) == "buy" else "sell"
        return self.history.loc[self.history["type"] == type, "closed"].all()

    def close_a_position(self, side: TSide, time_index: int, trade_amount: float):
        position_type = "long" if opp_side(side) == "buy" else "short"
        mask = (self.history["type"] == position_type) & (self.history["closed"] == False)
        idx = cast(int, self.history[mask].index[0])
        self.history.loc[idx, "closed"] = True
        self.history.loc[idx, "exit"] = trade_amount
        self.history.loc[idx, "exit_time"] = time_index
        entry = cast(float, self.history.iloc[idx]["entry"])
        revenue: float = trade_amount - entry
        self.history.loc[idx, "revenue"] = revenue if position_type == "long" else -revenue

    def update_history(self, side: TSide, time_index: int, trade_amount: float):
        if self.history.empty or self.all_positions_closed(side):
            self.history = self.history.append(dict(entry_time=time_index,
                                                    entry=trade_amount,
                                                    type="long" if side == "buy" else "short",
                                                    closed=False,
                                                    exit=None,
                                                    exit_time=None,
                                                    revenue=None),
                                               ignore_index=True)
        else:
            self.close_a_position(side, time_index, trade_amount)

    def print_results(self):
        if len(self.history) == 0:
            print("no trades made")
            return
        history = self.history
        display_df(DataFrame.from_records([dict(ind_size=len(self.individual))]))
        hold_times = history["exit_time"].sub(history["entry_time"])
        revenue = history["revenue"]
        total_revenue = revenue.sum()
        total_cost = history["entry"].sum()
        good_trades = history.loc[revenue > 0, "revenue"]
        bad_trades = history.loc[revenue < 0, "revenue"]
        long_trades = history[history["type"] == "long"]
        num_trades = len(history)
        data: Dict[str, Any] = dict(avg_hold_time=hold_times.mean(),
                                    roi=total_revenue / total_cost,
                                    num_trades=num_trades,
                                    total_revenue=total_revenue,
                                    percent_good=len(good_trades) / num_trades,
                                    percent_long=len(long_trades) / num_trades,
                                    best_trade=revenue.max(),
                                    worst_trade=revenue.min(),
                                    sum_pos=good_trades.sum(),
                                    sum_neg=bad_trades.sum())
        display_df(DataFrame.from_records([data]))
