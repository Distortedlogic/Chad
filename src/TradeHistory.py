from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, cast

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from old_src.api.dataframe import display_df
from src.Settings import TradeSettings


class ETradeSide(Enum):
    Buy = "buy"
    Sell = "sell"

    def opposite(self) -> 'ETradeSide':
        return ETradeSide.Buy if self is ETradeSide.Sell else ETradeSide.Sell


@dataclass
class TradeHistory:
    df = field(default_factory=lambda: DataFrame(columns=["entry",
                                                          "exit",
                                                          "type",
                                                          "closed",
                                                          "entry_time",
                                                          "exit_time",
                                                          "revenue"]))

    def get_score(self):
        self.remove_unclosed_trades()
        if len(self.df) < TradeSettings.MIN_NUM_TRADES or self.df["revenue"].std() == 0:
            return (-99999 + len(self.df),)
        return (self.calc_sqn(),)

    def calc_sqn(self) -> float:
        trade_num = len(self.df)
        revenue = self.df["revenue"]
        # q: float = revenue.quantile(0.95)
        # history = self.df[revenue < q]
        mean_profit: float = revenue.mean()
        std_profit = revenue.std()
        root_num_trades = trade_num ** 0.5
        amplifier = (root_num_trades / std_profit
                     if mean_profit < 0
                     else std_profit / root_num_trades)
        return amplifier * mean_profit

    def remove_unclosed_trades(self):
        self.df = self.df[self.df["closed"] == True]

    def all_positions_closed(self, eTradeSide: ETradeSide) -> bool:
        return self.df.loc[self.df["type"] == eTradeSide.opposite(), "closed"].all()

    def update_history(self, eTradeSide: ETradeSide, time_index: int, trade_amount: float):
        if self.df.empty or self.all_positions_closed(eTradeSide):
            self.df = self.df.append(dict(entry_time=time_index,
                                          entry=trade_amount,
                                          type=eTradeSide.value,
                                          closed=False,
                                          exit=None,
                                          exit_time=None,
                                          revenue=None),
                                     ignore_index=True)
        else:
            position_type = eTradeSide.opposite()
            mask = (self.df["type"] == position_type) & (self.df["closed"] == False)
            idx = cast(int, self.df[mask].index[0])
            self.df.loc[idx, "closed"] = True
            self.df.loc[idx, "exit"] = trade_amount
            self.df.loc[idx, "exit_time"] = time_index
            entry = cast(float, self.df.iloc[idx]["entry"])
            revenue: float = trade_amount - entry
            self.df.loc[idx, "revenue"] = revenue if position_type == ETradeSide.Buy else -revenue

    def print_results(self):
        if len(self.df) == 0:
            print("no trades made")
            return
        history = self.df
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

    def revenue_bars(self):
        revenue = self.df[self.df["closed"]]["revenue"]
        mean = revenue.mean()
        std = revenue.std()
        lower = int(mean - 3 * std)
        upper = int(mean + 3 * std)
        step = int(std) // 3
        if step == 0:
            return
        bins = sorted(list(range(lower, upper, step)) + [0])
        cuts: Series[float] = pd.cut(revenue, bins=bins, include_lowest=True, duplicates="drop")
        _ = cuts.value_counts(sort=False).plot.bar(rot=0, color="b", figsize=(15, 5))
        _ = plt.xticks(rotation=90)
        # plt.savefig("revenue_bar.png")
        plt.show()

    def plot_ec(self):
        _ = plt.figure(figsize=(15, 5))
        closed = self.df["closed"]
        revenue = self.df[closed]["revenue"]
        equity = revenue.cumsum()
        _ = plt.plot(equity)
        plt.savefig("equity_curve.png")
        plt.show()

    def plot_trades(prices: Series, history: DataFrame):
        _ = plt.figure(figsize=(15, 5))
        _ = plt.plot(prices, color="black", lw=2.0)
        _ = plt.plot(
            prices,
            "^",
            markersize=10,
            color="lime",
            label="long buy",
            markevery=(
                history.loc[history["type"] == "long", "entry_time"]
                .sort_values(by="entry_time")
                .astype(int)
                .to_list()
            ),
        )
        _ = plt.plot(
            prices,
            "^",
            markersize=10,
            color="darkgreen",
            label="short buy",
            markevery=(
                history.loc[history["type"] == "short", "exit_time"]
                .sort_values(by="exit_time")
                .astype(int)
                .to_list()
            ),
        )
        _ = plt.plot(
            prices,
            "v",
            markersize=10,
            color="orangered",
            label="long sell",
            markevery=(
                history.loc[history["type"] == "long", "exit_time"]
                .sort_values(by="exit_time")
                .astype(int)
                .to_list()
            ),
        )
        _ = plt.plot(
            prices,
            "v",
            markersize=10,
            color="darkred",
            label="short sell",
            markevery=(
                history.loc[history["type"] == "short", "entry_time"]
                .sort_values(by="entry_time")
                .astype(int)
                .to_list()
            ),
        )
        _ = plt.legend()
        plt.grid()
        # plt.savefig('trades.png')
        plt.show()
