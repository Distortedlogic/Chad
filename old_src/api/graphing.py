from typing import Any, List

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from deap import gp
from networkx.drawing.nx_agraph import graphviz_layout
from pandas.core.frame import DataFrame
from pandas.core.series import Series


def revenue_bars(history: DataFrame):
    revenue = history[history["closed"]]["revenue"]
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


def plot_ec(history: DataFrame):
    _ = plt.figure(figsize=(15, 5))
    closed = history["closed"]
    revenue = history[closed]["revenue"]
    equity = revenue.cumsum()
    _ = plt.plot(equity)
    plt.savefig("equity_curve.png")
    plt.show()


def graph(ind: List[Any]):
    plt.rcParams["figure.figsize"] = (150, 100)

    nodes, edges, labels = gp.graph(ind)
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    pos = graphviz_layout(g)

    _ = nx.draw_networkx_nodes(g, pos, node_size=200000, node_color="grey")
    _ = nx.draw_networkx_edges(g, pos)
    _ = nx.draw_networkx_labels(g, pos, labels, font_size=100)
    plt.savefig("graph.png")
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
