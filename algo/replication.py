import networkx as nx

class ReplicationUnit():
    def __init__(self, children, contained_nodes, replications):
        self.children = children
        self.contained_nodes = contained_nodes
        self.replications = replications

class ReplicationGraph():
    def __init__(self, node_query_mapping, node_graph, replication_tree):
        self.node_query_mapping = node_query_mapping
        self.node_graph = node_graph
        self.replication_tree = replication_tree

    @classmethod
    def from_query_graph(cls, query_graph, start_node):
        node_graph = query_graph.copy()
        top_lvl_unit = ReplicationUnit([], [], 1)
        mapping = {}
        for nd in node_graph.nodes:
            mapping[nd] = query_graph[nd]
            print(nd, node_graph[nd], query_graph[nd])
            top_lvl_unit.contained_nodes.append(nd)
            top_lvl_unit.children.append(ReplicationUnit([nd], [nd], 1))
        
        return cls(mapping, node_graph, top_lvl_unit)

