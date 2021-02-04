import networkx as nx

"""
get_graph will open the files at the given path, and parse them into a graph.
labels must start with a letter
"""
def get_graph(path):
    edge_path = f"{path}/edges.txt"
    lbls_path = f"{path}/labels.txt"

    with open(edge_path) as edges:
        relevant_lines = (l for l in edges if l[0].isdigit())
        g = nx.parse_adjlist(relevant_lines, nodetype=int)
    
    with open(lbls_path) as lbls:
        relevant_lines = (l for l in lbls if l[0].isalpha())
        for idx, l in enumerate(relevant_lines):
            g.nodes[idx+1]["lbl"] = l.strip()

    return g