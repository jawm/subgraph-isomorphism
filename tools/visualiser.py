import networkx as nx
import argparse
import parse
import matplotlib.pyplot as plt
import sys
sys.path.append("..")
from algo import sectree
from manual_sec_trees import q18

# visualise_graph will render a graph into a matplotlib axes
def visualise_graph(graph, ax):
    nx.draw(graph, ax=ax, with_labels=True, font_weight='bold', font_size=20, node_size=1000)

def visualise_sec_tree(sec_tree, ax):
    containers = _vis_structures(sec_tree.root_structure, 1)
    nodes = _vis_nodes(sec_tree.root_node)
    f = f"""digraph G {{
{containers}
{nodes}
}}"""

def _vis_structures(structure, tab):
    # todo properly partition the graph nodes in the label
    names = f"\n".join(f"{'    '*(tab+1)}{id(nd)} [label=\"{nd.label}\\n{nd.graph_nodes}\"]" for nd in structure.sec_nodes)
    subclusters = "\n".join(_vis_structures(s, tab + 1) for s in structure.children)
    template = f"""
{'    '*tab}subgraph cluster_{id(structure)} {{
{names}
{subclusters}
{'    '*tab}}}
    """
    return template

def _vis_nodes(node):
    s = "\n"
    for nd in node.children:
        s = s + f"    {id(node)} -> {id(nd)};\n"
        s = s + _vis_nodes(nd)
    return s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualise graphs')
    parser.add_argument('graph_id', help='name of the query graph')
    args = parser.parse_args()
    g = parse.get_graph(args.graph_id)
    fig = plt.figure()
    ax = fig.add_subplot(121)
    visualise_graph(g, ax)

    ax2 = fig.add_subplot(122)
    visualise_sec_tree(q18.sectree, ax)

    # fig.show()
    # input("press")

    sectree.get_SEC(g, 1)