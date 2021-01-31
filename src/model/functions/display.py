import IPython
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from networkx.drawing.nx_agraph import graphviz_layout


def print_history(history):
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        IPython.display.display(history)

def profit_bar(history):
    profits = history.loc[history["closed"], "profit"]
    lower = int(profits.mean() - 3 * profits.std())
    upper = int(profits.mean() + 3 * profits.std())
    step = int(profits.std()) // 3
    bins = sorted(list(range(lower, upper, step)) + [0])
    cuts = pd.cut(profits, bins=bins, include_lowest=True, duplicates="drop")
    ax = cuts.value_counts(sort=False).plot.bar(rot=0, color="b", figsize=(15, 5))
    plt.xticks(rotation=90)
    plt.savefig("profit_bar.png")
    plt.show()


def plot_ec(history):
    fig = plt.figure(figsize=(15, 5))
    equity = history.loc[history["closed"], "profit"].cumsum()
    plt.plot(equity)
    plt.savefig("equity_curve.png")
    plt.show()


def graph(ind):
    plt.rcParams["figure.figsize"] = (150, 40)

    nodes, edges, labels = gp.graph(ind)
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    pos = graphviz_layout(g)

    nx.draw_networkx_nodes(g, pos, node_size=20000, node_color="grey")
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos, labels, font_size=50)
    plt.savefig("graph.png")
    plt.show()


def plot_trades(prices, history):
    fig = plt.figure(figsize=(15, 5))
    plt.plot(prices, color="black", lw=2.0)
    plt.plot(
        prices,
        "^",
        markersize=10,
        color="lime",
        label="long buy",
        markevery=(
            history.loc[history["type"] == "long", "entry_time"]
            .sort_values()
            .astype(int)
            .to_list()
        ),
    )
    plt.plot(
        prices,
        "^",
        markersize=10,
        color="darkgreen",
        label="short buy",
        markevery=(
            history.loc[history["type"] == "short", "exit_time"]
            .sort_values()
            .astype(int)
            .to_list()
        ),
    )
    plt.plot(
        prices,
        "v",
        markersize=10,
        color="orangered",
        label="long sell",
        markevery=(
            history.loc[history["type"] == "long", "exit_time"]
            .sort_values()
            .astype(int)
            .to_list()
        ),
    )
    plt.plot(
        prices,
        "v",
        markersize=10,
        color="darkred",
        label="short sell",
        markevery=(
            history.loc[history["type"] == "short", "entry_time"]
            .sort_values()
            .astype(int)
            .to_list()
        ),
    )
    plt.legend()
    plt.grid()
    # plt.savefig('trades.png')
    plt.show()
