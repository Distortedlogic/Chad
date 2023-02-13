import hashlib
from typing import Any, List

import matplotlib.pyplot as plt
import networkx as nx
from deap import base, gp
from deap.gp import PrimitiveTree
from networkx.drawing.nx_agraph import graphviz_layout


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


class FitnessMax(base.Fitness):
    weights = (1.0,)


class Individual(PrimitiveTree):
    def __init__(self, content: Any):
        PrimitiveTree.__init__(self, content)
        self.fitness = FitnessMax()

    def __eq__(self, other: "Individual"):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return int(hashlib.sha256(self.__str__().encode("utf-8")).hexdigest(), 16)

