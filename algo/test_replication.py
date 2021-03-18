import networkx as nx
import unittest

from replication import ReplicationGraph, ReplicationUnit

class ReplicationTest(unittest.TestCase):
    def setUp(self):
        # TODO make this match our actual query graphs properly
        self.query = nx.Graph()
        self.query.add_nodes_from([1,2,3])
        self.query.add_edges_from([(1,2), (2, 3)])

    def test_construction(self):
        self.rg = ReplicationGraph.from_query_graph(self.query, 1)
        
        # verify that the node graph matches what we'd want
        self.assertTrue(nx.is_isomorphic(self.rg.node_graph, self.query))

        # verify that the replication tree matches what we'd want
        # 1. check the mapping has 1-1 for the nodes
        for nd, qnodes in self.rg.node_query_mapping.items():
            print(qnodes, type(qnodes))
            self.assertTrue(len(qnodes) == 1)
            self.assertTrue(qnodes[0] == nd)
        # 2. check the RNode graph is isomorphic to the query graph
        self.assertTrue(nx.is_isomorphic(self.rg.node_graph, self.query))
        # 3. check the ReplicationUnit tree is what we want
        desired = ReplicationUnit([
            ReplicationUnit([], [1], 1),
            ReplicationUnit([], [2], 1),
            ReplicationUnit([], [3], 1),
        ], [], 1)
        self.assertTrue(ReplicationUnit.isomorphic(self.rg, desired, self.rg.replication_tree))


if __name__ == "__main__":
    unittest.main()