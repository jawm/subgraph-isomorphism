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

    def outgoing_edges(self, rg):
        """
        returns an iterator of nodes in `rg.node_graph` which aren't in `self` but which are connected to it by an edge.
        """
        return (nbr for nd in self.sub_nodes() for nbr in rg.node_graph[nd] if nbr not in self.sub_nodes())

    def is_connected_to(self, rg, ru):
        ru_nodes = ru.sub_nodes()
        for nbr in self.outgoing_edges(rg):
            if nbr in ru_nodes:
                return True
        return False

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
        parent_rus = [] # RUs in `self` which are contained within `proposed_merges`
        children_ru = [] # RUs in `self` which descend from `parent_rus`
        children_parent_lookup = {} # maps from RUs in `children_ru` to the set of their parents in `parent_rus`
        proposed_merge_lookup = {} # maps from RUs in `self`, to groups in `proposed_merges`

        for merge_group in proposed_merges:
            for ru in merge_group:
                parent_rus.append(ru)
                proposed_merge_lookup[ru] = merge_group

        for parent_ru in parent_rus:
            for neighbour in parent_ru.outgoing_edges(self):
                if seen[neighbour]:
                    continue
                children_ru.append(self.node_ru_mapping[neighbour])

        print("CHILDREN", children_ru)
        print("PARENTS", parent_rus)
        print("LOOKUP", proposed_merge_lookup)

        # 2. Optimistically merging. 
        # Everything has now been merged in `children_ru`. Let's split it based on rules.

        # 2.1: each child has a set of parents, and a given child could only be merged with a sibling that has the same set of parents
        # So, if the parent set for child A differs from child B, they must get split apart
        proposed_merge_next = defaultdict(lambda: [])
        for child in children_ru:
            parents = frozenset(p for p in parent_rus if p.is_connected_to(self, child))
            children_parent_lookup[child] = parents
            proposed_merge_next[parents].append(child)

        # 2.2: each child must have the same number of outgoing edges as any sibling in its group
        # This makes the calculation for 2.3 easier, since it won't need to account for sibling connections.
        swap = defaultdict(lambda: [])
        for k, merge_group in proposed_merge_next.items():
            for ru in merge_group:
                out_edges = ru.outgoing_edges(self)
                out_count = sum(1 for _ in out_edges)
                swap[(k, out_count)].append(ru)
        proposed_merge_next = swap

        # 2.3 if the set of outgoing_edges for child A doesn't match that of sibling B then they cannot be merged
        # Sibling connections get filtered from the list of outgoing edges, since 2.3 will move nodes with such edges into different groups from those without.
        swap = defaultdict(lambda: [])
        for k, merge_group in proposed_merge_next.items():
            for ru in merge_group:
                out_edges = ru.outgoing_edges(self)
                outgoing = frozenset(edge for edge in out_edges if edge not in merge_group)
                swap[(k, outgoing)].append(ru)
        proposed_merge_next = swap

        # 2.4 if two nodes in a group are isomorphic then they should be in a group containing only isomorphic siblings
        swap = defaultdict(lambda: [])
        for k, merge_group in proposed_merge_next.items():
            # we'll repeatedly pull combinations out of the initial grouping until none are left
            while len(merge_group) > 0:
                group, label, merge_group = split_2_4(merge_group, self)
                swap[(k, label)].append(group)
        proposed_merge_next = swap

        # 3. We've now established proposed groups for the next recursive call. 
        # But first, we must verify that these new groups are compatible with the proposed groups that were passed to us
        # Now that the rules have been applied, we can look for any breaking splits that occurred.
        if len(proposed_merge_next) > len(proposed_merges):
            to_split = defaultdict(lambda: [])

            for _, group in proposed_merge_next.items():
                for ru in group:
                    # to_split[high_lvl_parent].append(high_lvl_parent.members)


                    for high_lvl_parent in parents:
                        split_out = set(mem for mem in high_lvl_parent.members if not sec_graph.has_edge(sec, mem))
                        to_split[high_lvl_parent].append(split_out)

            # this will be the thing we return to the higher level, which it can use to figure out how to proceed
            new_higher_lvl_secs = []
            for high_lvl_sec, split_outs in to_split.items():
                cp = high_lvl_sec.members.copy()
                while len(cp) > 0:
                    focus = cp[0]
                    contains = (g for g in split_outs if focus in g)
                    i = set(cp)
                    i = i.intersection(*contains) # we get the items which always appear with focus
                    i.add(focus) # in case none of split_outs thought they should include `m`. Not sure if this is actually possible.
                    no_contains = (g for g in split_outs if focus not in g)
                    i = i.difference(*no_contains) # remove any of the items which *also* appear not beside focus

                    # at this point, we can update split_outs to remove any nodes in `i` from it
                    for split_out in split_outs:
                        split_out.difference_update(i)

                    # we can also update the members list so that these items won't be considered any further. They've been added to an SEC
                    cp = [m for m in cp if m not in i]

                    # finally construct a new SEC with the split out items.
                    assert(len(i) > 0)
                    new_higher_lvl_secs.append(SEC(list(i), high_lvl_sec.label, high_lvl_sec.is_connected))
                    
            if len(new_higher_lvl_secs) > len(higher_level_secs): # > len(clusters):
                # print("pop", len(new_higher_lvl_secs), len(clusters))
                return new_higher_lvl_secs, None
        
        clusters[parents] = split_groups

        return None, False

def split_2_4(merge_group, rg):
    guide = merge_group[0]
    split_out = []
    group = [guide]
    grouped = None
    for ru in merge_group[1:]:
        if ReplicationUnit.isomorphic(rg, guide, ru):
            grouped = guide
            group.append(ru)
        else:
            split_out.append(ru)

    return group, grouped, split_out