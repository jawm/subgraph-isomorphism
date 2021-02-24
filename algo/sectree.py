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

global_id_counter = 0
class SEC:
    # members is a set of either SEC or graph nodes
    def __init__(self, members, label, is_connected):
        #sue me
        global global_id_counter
        self.global_id = global_id_counter
        global_id_counter += 1
        self.members = members
        self.label = label
        self.is_connected = is_connected
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
    sec_graph = nx.Graph()
    mapping = {}
    for nd in graph.nodes:
        mapping[nd] = SEC([nd], graph.nodes[nd]["lbl"], False)
        sec_graph.add_node(mapping[nd])

    for edge in graph.edges:
        sec_graph.add_edge(mapping[edge[0]], mapping[edge[1]])

    return (sec_graph, mapping[start_node])

def combine_structures(seen, sec_graph, higher_level_secs):
    """
    This recursive function will combine compatible parts of an sec_graph, producing a new sec_graph

    seen: a set of nodes in the sec_graph. If a node is in the set it has already been processed in this
        call to combine_structures. At the top level simply provide set with the start group as True
    sec_graph: a graph of SEC nodes which we want to combine
    clustered_groups: an array of groups, clustered based on which parents they descend from

    This function will return a new sec_graph, with the new groupings applied

    """

    # print("after 0.0", higher_level_secs)

    high_lvl_sec_mapping = {}

    groups = []
    for high_lvl_sec in higher_level_secs:
        for sec in high_lvl_sec.members:
            high_lvl_sec_mapping[sec] = high_lvl_sec
            groups.append(sec)

    # 1. combine all children from all groups
    
    # 1.1 we want these groups to be clustered so that all nodes in a group have the same set of parent groups
    # we will store as a dict, where the keys are tuples of the parent groups, and values are sets of groups
    clusters = defaultdict(lambda: defaultdict(lambda: []))

    # print("h", groups)

    for group in groups:
        for possible_child in sec_graph[group]:
            if possible_child in seen:
                continue

            parents = frozenset(high_lvl_sec_mapping[p] for p in sec_graph[possible_child] if p in seen)
            # todo at this point we actually want to check if the `parents` group is compat with higher_lvl_sec??

            if possible_child not in clusters[parents][possible_child.label]:
                clusters[parents][possible_child.label].append(possible_child)

    if len(clusters) == 0:
        # print("bottomed out?")
        g = nx.Graph()
        for high_lvl_sec in higher_level_secs:
            g.add_node(high_lvl_sec)


        # Add extra edges for sibling higher_lvl_secs which were siblings in the underlying graph
        ## TODO it might be possible to make this cheaper. Not certain, but maybe if *any* of the members have an edge, it would imply that all do? Or idk something yeh?
        for (idx, high_lvl_sec) in enumerate(higher_level_secs[:-1]):
            for high_lvl_sec2 in higher_level_secs[idx+1:]:
                q = False
                for sec in high_lvl_sec.members:
                    if q:
                        break
                    for sec2 in high_lvl_sec2.members:
                        if sec_graph.has_edge(sec, sec2):
                            q = True
                            break
                if q:
                    g.add_edge(high_lvl_sec, high_lvl_sec2)
        return higher_level_secs, g

    # print("after 1.1", clusters)
    
    # 2. Split up groups such that they satisfy our clustering rules.
    for parents, cluster in clusters.items():
        # 2.1 Nodes in a group must all have the same number of members in the underlying graph
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster.items():
            for sec in child_group:
                split_groups[f"{lbl}{len(sec.members)}"].append(sec)
        cluster1 = split_groups

        # 2.2 Nodes in a group must have the same degree
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster1.items():
            for sec in child_group:
                deg = nx.degree(sec_graph, sec)
                split_groups[f"{lbl}{deg}"].append(sec)
        cluster1 = split_groups

        # 2.3 Nodes in a group must have the same number of neighbours with each label
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster1.items():
            while True:
                lbl_matching_group, lbl_matching_counts, child_group = split_2_3(child_group, sec_graph)
                group_lbl = f"{lbl} -> " + ",".join(f"{k}:{v}" for k, v in sorted(lbl_matching_counts.items()))
                split_groups[group_lbl] = lbl_matching_group
                if len(child_group) == 0:
                    break
        cluster1 = split_groups

        # 2.4 If any nodes in the underlying graph were cliques, so must all nodes in this group
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster1.items():
            n = 0
            while True:
                matching_group, is_connected, child_group = split_2_4(child_group, sec_graph)
                l = "subc" if is_connected else "subu"
                split_groups[f"{lbl}{l}{n}"] = matching_group
                n += 1
                if len(child_group) == 0:
                    break
        cluster1 = split_groups

        # 2.5 If any nodes in a group are connected to each other, all nodes must be connected to each other.
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster1.items():
            n = 0
            while True:
                matching_group, is_connected, child_group = split_2_5(child_group, sec_graph)
                l = "c" if is_connected else "u"
                split_groups[f"{lbl}{l}{n}"] = (matching_group, is_connected)
                n += 1
                if len(child_group) == 0:
                    break
        
        
        
        # Now that the rules have been applied, we can look for any breaking splits that occurred.
        if len(split_groups) > len(cluster):
            to_split = defaultdict(lambda: [])

            for _, (group, is_connected) in split_groups.items():
                for sec in group:
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
                    

            if len(new_higher_lvl_secs) > len(clusters):
                return new_higher_lvl_secs, None
        
        clusters[parents] = split_groups

    # 3. Call combine structures one level lower
    next_seen = seen.copy()
    new_secs = []
    parent_lookup = {}
    for parents, cluster in clusters.items():
        groups_as_secs = []
        for lbl, (group, is_connected) in cluster.items():
            assert(len(group) > 0)
            s = SEC(group, group[0].label, is_connected)
            new_secs.append(s)
            groups_as_secs.append(s)
            for sec in group:
                parent_lookup[sec] = parents
                next_seen[sec] = True
        clusters[parents] = groups_as_secs
                

    need_split, new_graph = combine_structures(next_seen, sec_graph, new_secs)
    while len(need_split) > len(new_secs):
        new_secs = need_split
        to_split = defaultdict(lambda: [])
        for group in need_split:
            group = group.members
            for sec in group:
                # to_split[high_lvl_parent].append(high_lvl_parent.members)
                parents = parent_lookup[sec]
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

        if len(new_higher_lvl_secs) > len(higher_level_secs):
            return new_higher_lvl_secs, None
        else:
            need_split, new_graph = combine_structures(next_seen, sec_graph, new_secs)

    # 5. Add groups and edges to the graph
    for high_lvl_sec in higher_level_secs:
        # new_graph.add_node(high_lvl_sec) # todo we shouldn't have to do this... there should always be edges between things..
        for sec in high_lvl_sec.members:
            for new_sec in need_split:
                for s in new_sec.members:
                    if sec_graph.has_edge(sec, s):
                        new_graph.add_edge(high_lvl_sec, new_sec)

    

    return higher_level_secs, new_graph

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
    split_out = []
    group = [guide]
    for sec in child_group[1:]:
        if sec.is_connected == guide.is_connected:
            group.append(sec)
        else:
            split_out.append(sec)

    return group, guide.is_connected, split_out

def split_2_5(child_group, sec_graph):
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

    return group, is_connected, split_out

def get_SEC(graph, start_node):
    sec_graph, start = _build_initial_sec_graph(graph, start_node)

    # First argument doesn't matter here, since we know it will *never* be split
    print()
    print(visualise_SEC_graph(sec_graph, start))
    while True:
        s = SEC([start], start.label, False)
        _, new_sec_graph = combine_structures({start: True}, sec_graph, [s])
        if len(new_sec_graph) == len(sec_graph):
            break
        sec_graph = new_sec_graph
        start = s
        print()
        print(visualise_SEC_graph(sec_graph, start))

    return sec_graph

def simplify(sec_graph, start):
    m = {}
    for nd in sec_graph.nodes:
        m[nd] = simplify_sec(nd)

    return nx.relabel_nodes(sec_graph, m), m[start]

def simplify_sec(sec):
    if type(sec.members[0]) == int:
        return sec
    if len(sec.members) == 1:
        sec.members[0].global_id = sec.global_id
        s = simplify_sec(sec.members[0])
        s.global_id = sec.global_id
        return s
    for s in sec.members:
        s.global_id = sec.global_id
    v = [simplify_sec(s) for s in sec.members]
    for x in v:
        x.global_id = sec.global_id
    s = SEC(v, sec.label, sec.is_connected)
    s.global_id = sec.global_id
    return s

def visualise_SEC_graph(sec_graph, start):
    sec_graph, start = simplify(sec_graph, start)
    return f"""graph G {{
rankdir=LR
{_visualise_SEC_graph_nodes(sec_graph, start)}
{_visualise_SEC_graph_replications(0, sec_graph, sec_graph.nodes, 1)}
}}"""

def _visualise_SEC_graph_nodes(sec_graph, start):
    res = f"{start.global_id} [label=\"{start.label}\nconnected: {start.is_connected}\"]"
    for (nd, succ) in nx.bfs_successors(sec_graph, start):
        for n in succ:
            res = f"{res}\n{n.global_id} [label=\"{n.label}\nconnected: {n.is_connected}\"]"

    for (nd, nd2) in sec_graph.edges:
        res = f"{res}\n{nd.global_id}--{nd2.global_id};"

    return res

def _visualise_SEC_graph_replications(cluster_id, sec_graph, nodes, replications):
    res = f"""subgraph cluster_{cluster_id} {{
label= "replications: {replications}"
"""
    for nd in nodes:
        if len(nd.members) == 1:
            res = f"{res}\n{nd.global_id}"
        else:
            res = f"{res}\n{_visualise_SEC_graph_replications(cluster_id := cluster_id + 1, sec_graph, nd.members, len(nd.members))}"
    return f"{res}\n}}"
