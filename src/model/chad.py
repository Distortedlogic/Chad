import IPython
import pandas as pd
from deap import gp
from src.model.functions.calc import calc_sqn, opp_type


class Chad:
    def __init__(self, pset, df, max_trade_amount):
        self.pset = pset
        self.df = df
        self.hof_log = pd.DataFrame()
        self.max_trade_amount = max_trade_amount

    def fitness(self, individual):
        history = pd.DataFrame(
            columns=[
                "entry",
                "exit",
                "type",
                "closed",
                "entry_time",
                "exit_time",
                "revenue",
            ]
        )
        position = 0
        signals = gp.compile(individual, self.pset)(self.df)
        for time_index, row in signals.iterrows():
            amount = row["close"] * self.max_trade_amount
            if row["buy"] and self.can_trade(position):
                position += self.max_trade_amount
                history = self.update_history(history, "long", time_index, amount)
            elif row["sell"] and self.can_trade(position):
                position -= self.max_trade_amount
                history = self.update_history(history, "short", time_index, amount)
        history = history[history["closed"] == True]
        if len(history) < 30 or history.empty or history["revenue"].std() == 0:
            return (-99999 + len(history),)
        self.history = history
        return (calc_sqn(history),)

    @staticmethod
    def can_trade(position):
        return position > -1.1 and position < 1.1

    @staticmethod
    def update_history(history, type, time_index, trade_amount):
        if (
            history.empty
            or history.loc[history["type"] == opp_type(type), "closed"].all()
        ):
            history = history.append(
                dict(
                    entry_time=time_index,
                    entry=trade_amount,
                    type=type,
                    closed=False,
                    exit=None,
                    exit_time=None,
                    revenue=None,
                ),
                ignore_index=True,
            )
        else:
            mask = (history["type"] == opp_type(type)) & (history["closed"] == False)
            idx = history[mask].index[0]
            history.loc[idx, "closed"] = True
            history.loc[idx, "exit"] = trade_amount
            history.loc[idx, "exit_time"] = time_index
            trade = history.iloc[idx]
            long_rev = trade_amount - trade["entry"]
            history.loc[idx, "revenue"] = long_rev if type == "long" else -long_rev
        return history

    def print_results(self):
        history = self.history
        self.hof_log = self.hof_log.append(
            dict(
                avg_hold_time=history["exit_time"].sub(history["entry_time"]).mean(),
                roi=history["revenue"].sum() / history["entry"].sum(),
                num_trades=len(history),
                total_revenue=history["revenue"].sum(),
                percent_good=len(history[history["revenue"] > 0]) / len(history),
                percent_long=len(history[history["type"] == "long"]) / len(history),
                best_trade=history["revenue"].max(),
                worst_trade=history["revenue"].min(),
                sum_pos=history.loc[history["revenue"] > 0, "revenue"].sum(),
                sum_neg=history.loc[history["revenue"] < 0, "revenue"].sum(),
            ),
            ignore_index=True,
        )
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            IPython.display.display(self.hof_log[-1:])
