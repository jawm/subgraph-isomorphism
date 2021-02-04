from algo.sectree import *

start_node = 1

a = EquivalentNodeGroup('a', [0])
b = EquivalentNodeGroup('b', [1,2,3,4])
c = EquivalentNodeGroup('c', [5,6])
d = EquivalentNodeGroup('d', [7])
e = EquivalentNodeGroup('e', [8])

c1 = ReplicatedStructure(1, [a, d, e])
c2 = ReplicatedStructure(2, [c])
c3 = ReplicatedStructure(2, [b])

a.add_child(b)
b.add_child(c)
b.add_child(e)
c.add_child(d)

c1.add_child(c2)
c2.add_child(c3)

sectree = SECTree(c1, a)