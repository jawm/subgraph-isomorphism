import networkx as nx
import itertools

class ReplicationUnit():
    def __init__(self, children, contained_nodes, replications):
        self.children = children
        self.all_contained_nodes = contained_nodes + list(itertools.chain(*(x.sub_nodes() for x in children)))
        self.contained_nodes = contained_nodes
        self.replications = replications

    def sub_nodes(self):
        return self.all_contained_nodes

    @staticmethod
    def isomorphic(RG, RU1, RU2):
        if RU1.replications != RU2.replications:
            return False
        if len(RU1.children) != len(RU2.children):
            return False
        if len(RU1.all_contained_nodes) != len(RU2.all_contained_nodes):
            print(RU1.all_contained_nodes, RU2.all_contained_nodes)
            return False
        return nx.is_isomorphic(RG.node_graph.subgraph(RU1.all_contained_nodes), RG.node_graph.subgraph(RU2.all_contained_nodes))

class ReplicationGraph():
    def __init__(self, start_node, node_query_mapping, node_graph, replication_tree):
        self.start_node = start_node
        self.node_query_mapping = node_query_mapping
        self.node_graph = node_graph
        self.replication_tree = replication_tree

    @classmethod
    def from_query_graph(cls, query_graph, start_node):
        node_graph = query_graph.copy()
        
        mapping = {}
        children = []
        for nd in node_graph.nodes:
            mapping[nd] = [nd]
            print(nd, node_graph[nd], query_graph[nd])
            children.append(ReplicationUnit([], [nd], 1))
        top_lvl_unit = ReplicationUnit(children, [], 1)

        return cls(start_node, mapping, node_graph, top_lvl_unit)

