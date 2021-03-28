from collections import defaultdict
import networkx as nx
import itertools

class ReplicationUnit():
    def __init__(self, children, contained_nodes, replications, parent):
        self.parent = parent
        self.children = children
        self.contained_nodes = contained_nodes
        self.replications = replications

    def highest_parent(self):
        if self.parent != None:
            return self.parent.highest_parent()
        return self

    def sub_nodes(self):
        return self.contained_nodes + list(itertools.chain(*(x.sub_nodes() for x in self.children)))

    @staticmethod
    def isomorphic(RG, RU1, RU2):
        if RU1.replications != RU2.replications:
            return False
        if len(RU1.children) != len(RU2.children):
            return False
        if len(RU1.sub_nodes()) != len(RU2.sub_nodes()):
            return False
        return nx.is_isomorphic(RG.node_graph.subgraph(RU1.sub_nodes()), RG.node_graph.subgraph(RU2.sub_nodes()))

class ReplicationGraph():
    def __init__(self, start_node, node_query_mapping, node_graph, node_ru_mapping):
        self.start_node = start_node
        self.node_query_mapping = node_query_mapping
        self.node_ru_mapping = node_ru_mapping
        self.node_graph = node_graph
        
    def lowest_common_ancestor(self, root, nd1, nd2):
        for contained_nd in root.contained_nodes:
            if contained_nd == nd1 or contained_nd == nd2:
                # this should only really happen at the top call if one of the nodes was directly contained in the root container.
                return root

        for ru in root.children:
            if nd1 in ru.all_contained_nodes:
                nd1_container = ru
            if nd2 in ru.all_contained_nodes:
                nd2_container = ru

        if nd1_container == nd2_container:
            return self.lowest_common_ancestor(nd1_container, nd1, nd2)
        else:
            return root, nd1_container, nd2_container

    @classmethod
    def from_query_graph(cls, query_graph, start_node):
        node_graph = query_graph.copy()
        
        mapping = {}
        nd_ru_mapping = {}
        for nd in node_graph.nodes:
            mapping[nd] = nd
            ru = ReplicationUnit([], [nd], 1, None)
            nd_ru_mapping[nd] = ru
        
        return cls(start_node, mapping, node_graph, nd_ru_mapping)

    def simplify(self):
        return self._recursive_simplify(defaultdict(bool, {self.start_node: True}), [[self.node_ru_mapping[self.start_node]]])

    def _recursive_simplify(self, seen, proposed_merges):
        """
        _recursive_simlify will return a simplified version of self as a ReplicationGraph
        This simplified version will merge ReplicationUnits which are considered compatible. 
        The function operated recursively in a BFS manner, with all RUs from the same "generation" of the BFS being processed together.
        
        `seen` indicates which nodes have already been handled in higher level calls (since this is recursive)
            This is structured as a dictionary, mapping RUs to a bool. True indicates that it has been seen, and should therefore not be considered.

        `proposed_merges` indicates how the direct caller proposes to merge the RUs which it operated on (so only the RUs from a single generation of the BFS)
            This is structured as a list of lists of RUs. RUs that are together are proposed to be merged into a single RU in the final simplified result

        
        """

        # 1. firstly, we need to identify the list of children which are descending from the things in proposed_merges
        children_ru = []
        for merge_group in proposed_merges:
            for ru in merge_group:
                # We want to find edges which start in ru, and end outside it.
                # For each of those edges, look at the ru it ends in.
                # If this destination is in `seen`, we can continue. 
                # Otherwise, it is a child of the ru, and so is something we are going to be attempting to merge.
                
                # So first, we loop over all edges, to do that we loop over the contained nodes
                for nd in ru.sub_nodes():
                    for neighbour in self.node_graph[nd]:
                        # If neighbour is in `seen`, not a child
                        if seen[neighbour]:
                            continue
                        # If neighour within ru, not a child
                        if neighbour in ru.sub_nodes():
                            continue
                        # now we know it is a child, so get the associated RU, and add it as child.
                        children_ru.append(self.node_ru_mapping[nd])

        return None, False