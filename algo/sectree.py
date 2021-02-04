from collections import defaultdict
from matplotlib import patches
import networkx as nx

class SECTree:
    def __init__(self, root_structure, root_node):
        self.root_structure = root_structure
        self.root_node = root_node

class EquivalentNodeGroup:
    def __init__(self, label, graph_nodes):
        self.label = label
        self.graph_nodes = graph_nodes
        self.children = []

    def add_child(self, sec_node):
        self.children.append(sec_node)

class ReplicatedStructure:
    def __init__(self, replications, sec_nodes):
        self.replications = replications
        self.sec_nodes = sec_nodes
        self.children = []

    def add_child(self, replicated_structure):
        self.children.append(replicated_structure)


"""

Ok, let's get serious now

Below is code relating to my new idea seen in notes 3

"""

class SEC:
    # members is a set of either SEC or graph nodes
    def __init__(self, members, label):
        self.members = members
        self.label = label
        self.children = []

    def add_child(self, sec):
        self.children.append(sec)

    def is_node(self):
        return False

class Nd:
    def __init__(self, graph_node):
        self.graph_node = graph_node

    def is_node(self):
        return True

def _build_initial_sec_graph(graph, start_node):
    sec_graph = nx.Graph() # todo maybe this should be directed?
    mapping = {}
    for nd in graph.nodes:
        mapping[nd] = SEC([nd], graph.nodes[nd]["lbl"])
        sec_graph.add_node(mapping[nd])

    for edge in graph.edges:
        sec_graph.add_edge(mapping[edge[0]], mapping[edge[1]])

    return (sec_graph, mapping[start_node])

def combine_structures(seen, sec_graph, groups):
    """
    This recursive function will combine compatible parts of an sec_graph, producing a new sec_graph

    seen: a set of nodes in the sec_graph. If a node is in the set it has already been processed in this
        call to combine_structures. At the top level simply provide set with the start group as True
    sec_graph: a graph of SEC nodes which we want to combine
    groups: the groups we actually want to work on now.

    This function will return a new sec_graph, with the new groupings applied

    """


    # 1. combine all children from all groups
    
    # 1.1 we want these groups to be clustered so that all nodes in a group have the same set of parent groups
    # we will store as a dict, where the keys are tuples of the parent groups, and values are sets of groups
    known_parent_clusters = defaultdict(lambda: set())

    for group in groups:
        for possible_child in sec_graph[group]:
            if possible_child in seen:
                continue
            parents = tuple(p for p in sec_graph[possible_child] if p in seen)
            known_parent_clusters[parents].add(possible_child)

    print("after 1.1", known_parent_clusters)
    
    # todo probably remove below code
    # child_groups = defaultdict(lambda: [])
    # for group in groups:
    #     for neighbour in sec_graph[group]:
    #         if neighbour in seen:
    #             continue
    #         child_groups[neighbour.label].append(neighbour)

    # 2. split children according to rules
    
    # 2.1 Nodes in a group must have the same label
    # When building the set of children groups we developed this already, so no changes need made

    print("after 2.1", child_groups)

    # 2.2 Nodes in a group must have the same degree
    child_groups_swap = defaultdict(lambda: [])
    for lbl, child_group in child_groups.items():
        for sec in child_group:
            deg = nx.degree(sec_graph, sec)
            child_groups_swap[f"{sec.label}{deg}"].append(sec)
    child_groups = child_groups_swap

    print("after 2.2", child_groups)

    # 2.3 Nodes in a group must have the same number of neighbours with each label
    child_groups_swap = defaultdict(lambda: [])
    for lbl, child_group in child_groups.items():
        while True:
            lbl_matching_group, lbl_matching_counts, child_group = split_2_3(child_group, sec_graph)
            group_lbl = "_".join(f"{k}:{v}" for k, v in sorted(lbl_matching_counts.items()))
            child_groups_swap[group_lbl] = lbl_matching_group
            if len(child_group) == 0:
                break
    child_groups = child_groups_swap

    print("after 2.3", child_groups)

    # 2.4 If any nodes in a group are connected to each other, all nodes must be connected to each other.
    child_groups_swap = defaultdict(lambda: [])
    for lbl, child_group in child_groups.items():
        n = 0
        while True:
            matching_group, matching_lbl, child_group = split_2_4(child_group, sec_graph)
            child_groups_swap[f"{lbl}{matching_lbl}{n}"] = matching_group
            n += 1
            if len(child_group) == 0:
                break

    child_groups = child_groups_swap

    print("after 2.4", child_groups)

    # 3. if a split broke things, then split that thing in next_graph, return False

    # 4. else call combine structures one level lower

    # 5. return all generated groups... as a graph somehow??

def split_2_3(child_group, sec_graph):
    neighbours = sec_graph[child_group[0]]
    counts = defaultdict(lambda: 0)
    for nd in neighbours:
        counts[nd.label] += 1
    split_out = []
    group = [child_group[0]]
    for sec in child_group[1:]:
        if split_2_3_breaker(counts, sec_graph, sec):
            split_out.append(sec)
        else:
            group.append(sec)
    return child_group, counts, split_out

def split_2_3_breaker(counts, sec_graph, sec):
    neighbours1 = sec_graph[sec]
    counts1 = defaultdict(lambda: 0)
    for nd in neighbours1:
        counts1[nd.label] += 1
    for lbl, count in counts.items():
        if count != counts1[lbl]:
            return True
    for lbl, count in counts1.items():
        if count != counts[lbl]:
            return True
    return False

def split_2_4(child_group, sec_graph):
    guide = child_group[0]

    is_connected = False
    for sec in child_group[1:]:
        if sec_graph.has_edge(guide, sec):
            is_connected = True
            break

    split_out = []
    group = [child_group[0]]
    for sec in child_group[1:]:
        if sec_graph.has_edge(guide, sec) != is_connected:
            split_out.append(sec)
        else:
            group.append(sec)

    return group, "c" if is_connected else "u", split_out

def get_SEC(graph, start_node):
    sec_graph, start = _build_initial_sec_graph(graph, start_node)

    # First argument doesn't matter here, since we know it will *never* be split
    while True:
        combine_structures({start: True}, sec_graph, [start])
        # TODO uncomment below code instead of above single line
        # sec_graph = combine_structures({}, sec_graph, [start])
        # if nx.algorithms.is_tree(sec_graph): # todo work out how to call this
        #     break
        break

    return sec_graph