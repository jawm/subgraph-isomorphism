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
    def __init__(self, members, label):
        #sue me
        global global_id_counter
        self.global_id = global_id_counter
        global_id_counter += 1
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
    sec_graph = nx.Graph()
    mapping = {}
    for nd in graph.nodes:
        mapping[nd] = SEC([nd], graph.nodes[nd]["lbl"])
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

    high_lvl_sec_mapping = {} # defaultdict(lambda: set())

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
        return higher_level_secs, g

    # print("after 1.1", clusters)
    
    # 2.1 Nodes in a group must have the same label
    # When building the set of children groups we developed this already, so no changes need made

    # print("after 2.1", clusters)

    # 2.2 Nodes in a group must have the same degree
    for parents, cluster in clusters.items():
        # print("hello", parents, cluster)
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster.items():
            for sec in child_group:
                deg = nx.degree(sec_graph, sec)
                split_groups[f"{sec.label}{deg}"].append(sec)
        # at this point, the child groups may have been split
        # if they have, we need to check if that's going to trigger a split in the parents. 
        # if it does we'll return a result indicating that to the caller?
        if len(split_groups) > len(cluster):
            print("a split occurred 2.2")
            # TODO actually do something here
        clusters[parents] = split_groups

    # print("after 2.2", clusters)

    # 2.3 Nodes in a group must have the same number of neighbours with each label
    for parents, cluster in clusters.items():
        print("hello", parents, cluster)
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster.items():
            while True:
                lbl_matching_group, lbl_matching_counts, child_group = split_2_3(child_group, sec_graph)
                group_lbl = f"{lbl} -> " + ",".join(f"{k}:{v}" for k, v in sorted(lbl_matching_counts.items()))
                split_groups[group_lbl] = lbl_matching_group
                if len(child_group) == 0:
                    break
        if len(split_groups) > len(cluster):
            print("a split occured 2.3")

            for group in split_groups:
                print(group)
            
            to_split = defaultdict(lambda: [])

            for _, group in split_groups.items():
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
                    new_higher_lvl_secs.append(SEC(list(i), high_lvl_sec.label))
                    

            if len(new_higher_lvl_secs) > len(clusters):
                return new_higher_lvl_secs, None


            ### -----


            # start by getting all the parents in the higher_lvl_sec for each group.
            # group_parent_sets = []
            # for _, group in split_groups.items():
            #     group_all_higher_lvl_parents = set()
            #     for sec in group:
            #         higher_lvl_parents = set(high_lvl_sec_mapping[p] for p in sec_graph[sec] if p in seen)
            #         group_all_higher_lvl_parents = group_all_higher_lvl_parents.union(higher_lvl_parents)
            #     group_parent_sets.append(group_all_higher_lvl_parents)

            # # once we have that we want to find all common parents from each group.
            # # we keep looping until we've got it fully split out
            # idx = 0
            # while idx < len(group_parent_sets):
            #     s = group_parent_sets[idx]
            #     for parent_set in group_parent_sets[idx+1:]:
            #         s = s.intersection(parent_set)
            #     if len(s) == 0:
            #         idx += 1
            #         continue
            #     group_parent_sets.append(group_parent_sets[idx].copy())
            #     group_parent_sets[idx] = s
            #     for parent_set in group_parent_sets[idx+1:]:
            #         parent_set.difference_update(s)
            #     idx += 1

            # print(group_parent_sets)
            # print(higher_level_secs)
            # if len(group_parent_sets) > len(higher_level_secs):
            #     print("i think it broken yeh")
            #     for sec in higher_level_secs:
            #         print("broke parent", sec.label)
        clusters[parents] = split_groups

    # print("after 2.3", clusters)

    # 2.4 If any nodes in a group are connected to each other, all nodes must be connected to each other.
    for parents, cluster in clusters.items():
        # print("hello", parents, cluster)
        split_groups = defaultdict(lambda: [])
        for lbl, child_group in cluster.items():
            n = 0
            while True:
                matching_group, matching_lbl, child_group = split_2_4(child_group, sec_graph)
                split_groups[f"{lbl}{matching_lbl}{n}"] = matching_group
                n += 1
                if len(child_group) == 0:
                    break
        if len(split_groups) > len(cluster):
            print("a split occured 2.4")
            
            # start by getting all the parents in the higher_lvl_sec for each group.
            group_parent_sets = []
            for _, group in split_groups.items():
                group_all_higher_lvl_parents = set()
                for sec in group:
                    higher_lvl_parents = set(high_lvl_sec_mapping[p] for p in sec_graph[sec] if p in seen)
                    group_all_higher_lvl_parents = group_all_higher_lvl_parents.union(higher_lvl_parents)
                group_parent_sets.append(group_all_higher_lvl_parents)
            
            # once we have that we want to find all common parents from each group.
            # we keep looping until we've got it fully split out
            new_parent_high_lvl_secs = []
            idx = 0
            while idx < len(group_parent_sets):
                s = group_parent_sets[idx]
                for parent_set in group_parent_sets[idx+1:]:
                    s = s.intersection(parent_set)
                if len(s) == 0:
                    idx += 1
                    continue
                group_parent_sets.append(group_parent_sets[idx].copy())
                group_parent_sets[idx] = s
                for parent_set in group_parent_sets[idx+1:]:
                    parent_set.difference_update(s)
                idx += 1

            if len(new_parent_high_lvl_secs) > len(higher_level_secs):
                print("i think it broken yeh")

            # at this point we know that a group got split, since there's more than there was previously
            # so, what we'll do is loop over the new groups
            # for each of these groups, we check that it is still connected to *all* parents
            # if there is any of the parents to which it is not connected, then a breaking split has occured and it will need propagated
            # todo this is actually all wrong, since the sec_graph input is already known to be correct. instead we want to check if there was a split in the higher_level_secs or something
            # for _, group in split_groups.items():
            #     for sec in group:
            #         for parent in parents:
            #             # print("checking edge", sec, parent)
            #             if not sec_graph.has_edge(sec, parent):
            #                 print("BREAKING SPLIT OCCURRED THIS IS NOT A DRILL")
            # print("after the breaking split check...")
        clusters[parents] = split_groups

    # print("after 2.4", clusters)

    # 3. if a split broke things, then split that thing in next_graph, return False

    # 4. else call combine structures one level lower
    next_seen = seen.copy()
    new_secs = []
    parent_lookup = {}
    for parents, cluster in clusters.items():
        groups_as_secs = []
        for lbl, group in cluster.items():
            assert(len(group) > 0)
            s = SEC(group, group[0].label)
            new_secs.append(s)
            groups_as_secs.append(s)
            for sec in group:
                parent_lookup[sec] = parents
                next_seen[sec] = True
        clusters[parents] = groups_as_secs
                

    need_split, new_graph = combine_structures(next_seen, sec_graph, new_secs)
    while len(need_split) > len(new_secs):
        print("DEALING WITH A SPLIT THAT GOT PASSED UP")
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
                new_higher_lvl_secs.append(SEC(list(i), high_lvl_sec.label))

        if len(new_higher_lvl_secs) > len(higher_level_secs):
            print("going one way")
            return new_higher_lvl_secs, None
        else:
            print("going another")
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
    print()
    print(visualise_SEC_graph(sec_graph, start))
    while True:
        s = SEC([start], start.label)
        _, new_sec_graph = combine_structures({start: True}, sec_graph, [s])
        if len(new_sec_graph) == len(sec_graph):
            break
        sec_graph = new_sec_graph
        start = s
        print()
        print(visualise_SEC_graph(sec_graph, start))

    return sec_graph

def visualise_SEC_graph(sec_graph, start):
    return f"""digraph G {{
{_visualise_SEC_graph_rec({start: True}, sec_graph, [start])}
}}"""

def _visualise_SEC_graph_rec(seen, sec_graph, nodes):
    res = ""
    next_seen = seen.copy()
    nodes2 = []
    for nd in nodes:
        res = f"{res}\n{nd.global_id} [label=\"{nd.label}\"]"
        # print(nd, nd.label, nd.members)
        # for x in sec_graph.nodes:
        #     print("in graph", x.label, x.members, x)
        for nd2 in sec_graph[nd]:
            if nd2 in seen:
                continue
            res = f"{res}\n{nd.global_id}->{nd2.global_id};"
            # for nd2 in sec_graph.nodes:
            #     if nd not in seen:
            #         continue
            #     res = f"{res}\n{nd2.global_id}->{nd.global_id};"
            next_seen[nd2] = True
            if nd2 in nodes2:
                continue
            nodes2.append(nd2)
    if len(nodes2) > 0:
        res = f"{res}\n{_visualise_SEC_graph_rec(next_seen, sec_graph, nodes2)}"

    return res
