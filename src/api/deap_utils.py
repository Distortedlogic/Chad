import inspect

import matplotlib.pyplot as plt
import networkx as nx
from deap import gp
from networkx.drawing.nx_agraph import graphviz_layout


def graph(ind):
    plt.rcParams["figure.figsize"] = (50, 40)

    nodes, edges, labels = gp.graph(ind)
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    pos = graphviz_layout(g)

    nx.draw_networkx_nodes(g, pos, node_size=20000, node_color='grey')
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos, labels, font_size=50)
    plt.savefig('graph.png')
    plt.show()
