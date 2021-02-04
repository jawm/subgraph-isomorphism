I think the first phase of this project will be to come up with a bunch of 
examples of translating query graphs into SECTrees. This translation process
does somewhat depend upon the data graph for selection of the start nodes in
the transformation process, but to keep things easy to test and develop in
independent stages I will hardcode start nodes for these transformations.

The idea is that once I have a bunch of test cases, I can start working on an
algorithm to try and correctly generate the SECTrees automatically, and be 
able to verify it's correctness.

Manually going through this process should also help me to get a better 
understanding of the SECTree and the process of generating it from a query
graph.

I think I will get these query graphs from my uni project.

I'll also maybe make a couple of tools for visualising the graphs and SECTrees
which should be handy during this process also.