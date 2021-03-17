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
        self.replication_graph = ReplicationGraph.from_query_graph(self.query, 1)
        
        # verify that the node graph matches what we'd want
        self.assertTrue(nx.is_isomorphic(self.replication_graph.node_graph, self.query))

        # verify that the replication tree matches what we'd want
        desired = ReplicationUnit([], [], 1)

if __name__ == "__main__":
    unittest.main()