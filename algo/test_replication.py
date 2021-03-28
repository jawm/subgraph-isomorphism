import networkx as nx
import unittest

from replication import ReplicationGraph, ReplicationUnit

class ReplicationTest(unittest.TestCase):
    def setUp(self):
        # TODO make this match our actual query graphs properly
        self.query1 = nx.Graph()
        self.query1.add_nodes_from([1,2,3])
        self.query1.add_edges_from([(1,2), (2, 3)])

        self.query2 = nx.Graph()
        self.query2.add_nodes_from([1,2,3,4,5])
        self.query2.add_edges_from([(1,2), (2, 3), (1, 4), (3, 5)])

    def test_construction(self):
        rg = ReplicationGraph.from_query_graph(self.query1, 1)
        
        # verify that the node graph matches what we'd want
        self.assertTrue(nx.is_isomorphic(rg.node_graph, self.query1))

        # verify that the replication tree matches what we'd want
        # 1. check the mapping has 1-1 for the nodes
        for nd, qnodes in rg.node_query_mapping.items():
            self.assertTrue(len(qnodes) == 1)
            self.assertTrue(qnodes[0] == nd)
        # 2. check the RNode graph is isomorphic to the query graph
        self.assertTrue(nx.is_isomorphic(rg.node_graph, self.query1))
        # 3. check the ReplicationUnit tree is what we want
        desired = ReplicationUnit([
            ReplicationUnit([], [1], 1),
            ReplicationUnit([], [2], 1),
            ReplicationUnit([], [3], 1),
        ], [], 1)
        self.assertTrue(ReplicationUnit.isomorphic(rg, desired, rg.replication_tree))

    def test_simplify(self):
        rg = ReplicationGraph.from_query_graph(self.query1, 1)
        simplified, changed = rg.simplify()
        self.assertFalse(changed)

        rg = ReplicationGraph.from_query_graph(self.query2, 1)
        simplified, changed = rg.simplify()
        self.assertTrue(changed)


if __name__ == "__main__":
    unittest.main()
