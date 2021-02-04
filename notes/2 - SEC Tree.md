So, with the SEC Tree, I think if we can work out how to even represent it in
memory, that will probably get us a good understanding on writing an 
algorithm for generating them.

Let's consider Figure 3-5 of my Research report.

It may make more sense to consider nodes u1, u4 and u5 as actually being in 
different containers. Essentially making the idea that the hierarchy of the
containers is separate from that of the nodes. The nodes must form a tree, but
the containers can be arranged such that they nest inside each other, or 
coexist as siblings. That probably doesn't make much sense written down...

Although... for the sake of having some sort of top level thing maybe it is
easier to work with a single "top level" container. It's all rather confusing.

Note that querytest 18 is basically the same as Figure 3 except there is edges
between the Bs, u2->u3, and u4->u5.

