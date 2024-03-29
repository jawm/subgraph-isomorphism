Let's maybe put down some pseudo code for the conversion now that we've got
some basic visualisations happening.

So we take the start node as given.

The start node will correspond directly to an EquivalentNodeGroup in the 
SECTree, with just that single node in the group. The top level container will
therefore also have just one replication.

From the start node we explore all the children. I think what we'd do is start
with them all together in a single set, which we then break down based on 
various checks. 

Firstly, and obviously you split based on label. Nodes with different labels 
aren't symmetric.

Then you split based on the degree of the node. So now, nodes will be in 
groups with other nodes that have the same degree AND the same label.

Then you separate the groups based on the number of neighbours to a given node
with a given label. So kind of like the degree but specific to each label of 
neighbours. So, at this point you'd have groups where all nodes in the group 
have the same label, and have the same number of neighbours with each label.

Now we probably want to ensure that if nodes in a group are connected to each 
other, then we split off from any other nodes which aren't connected. I.e if 
any of the nodes in a group are connected to each other, then the nodes in 
that group must form a fully connected subgraph of the query.

Now is the hard part.... HOW do we make this above recurse downwards. We need
a way for the children of nodes in a group to be able to report that they 
aren't compatible in such a way that the nodes in the parent group must be 
split up into separate groups.

Maybe what we do, is combine all the children of a group into a full group, 
then repeat the above steps. So we're not looking at children of each member
of the group individually, but rather at all children of all members together.

Then, when we get the groupings back, if there was a split .... do something?

Actually, maybe we could get all children of all groups together, since we're
trying to do a breadth first type algorithm. We pre-split them based on which
of the group they descend from. If there are nodes which descend from multiple
groups, then they get put into a group with any other nodes that join that 
descend from the same set of groups?

Once we've got this big bunch of groups, we apply the initial splitting 
process once again, keeping track of which parent group(s) a child group 
descends from.

Once we have these child groupings, we see whether they would cause a split
of their parents at all. We determine this by saying that if the nodes in a 
child group only descend from some of the nodes in a parent group, then there
should be a split in the parent group, such that all nodes in the split-off 
group are still going to be parents of the child group. At this point we maybe
rerun the entire child splitting process??? Not 100% if that is necessary, but
I think it might be, and it at least doesn't do any harm (other than wasted
cycles). Yeah I'm thinking that this is probably necessary, since the new
parent split could reveal splits in the child groups that may not have 
otherwise appeared. Another important thing is that if a parent group gets
split, then you will have to go back up the structure and start again with the
new splittings for *that* set of groups too, and so on.

Now the question is, how do we actually arrange this process. Like it feels 
like there is going to have to be some sort of recursive nature to it, but I'm
not sure how the backtracking stuff fits into that...

I suppose that once a backtrack is noticed as being necessary, you would 
perform the split of the parent grouping, but then completely wipe the child
groupings, and wind back up the stack with some sort of 'error' type result 
that indicates a splitting took place. At this point, we again perform the 
assessment of whether it is necessary to split further. If so we perform the
same process recursively of splitting the current parent appropriately, then 
returning a signal up the stack indicating that a split has been occurred 
which needs checked.

This whole shit is kind of complicated, but I legit think it's most of the
algorithm. Now I also need to work out how we ultimately convert this tree
of groupings into an SECTree. In particular, I'm not sure how we sort the 
whole thing into the containers, and work out what the replications for those
containers should be. It's complicated, but I think it should maybe fall into
place somewhat naturally.

Anyway, that is (I hope) some really good progress. Bedtime.


--- The next day ---

Ok, upon review I'm pretty sure the above algorithm works for giving us a 
hierarchy of symmetric groupings, however it's not an SECTree. Of course, we
don't want to be too wed to our current understanding of the SECTree, since it
might not be the most useful way of structuring our data. That being said, I 
think that the group hierarchy is probably not useful on it's own.

Crazy idea but... maybe you could just run the whole process again, but this 
time on the group hierarchy itself. Basically treat each group as an 
individual node in a graph, and then see which things get grouped together.
Anything which is grouped together forms a structural equivalence thingy???

Ok maybe we do this:

You start by forming a graph of node groupings which matches the original 
query graph. Each node-group only includes a single node, so each group will
correspond to a single node.

Then you run through the process I described yesterday.

Start with the group that contains our designated starting node.

Always mark groups at the current level as being 'seen'.

Optimisitcally try to merge all groups at the level below, then split them 
based on the rules described. After each split, check whether it "breaks" the
parent groups apart. If so, split that parent group. Mark groups in the layer
below as unseen, then repeat.

Once you reach the bottom of the graph you basically repeat the process by 
wrapping all the groups inside groups again, then start over.

Keep doing this until you have a tree (or maybe until nothing changes, but I 
think that's maybe the same thing??).

At this point, you will have groups that form a tree. Each group could contain
other groups, or at the bottom level contain nodes.

I'm thinking that this actually replaces my idea for an SECTree, but we'll 
see.

Another important rule which this will necessitate:

When splitting the child groups, you should also split on: how many contained
groups there are, and whether they are fully connected?? I think so - there's
definitely going to be some sort of restriction like that...

... some time passes ...

Ok so I'm getting through some of the splitting rules and everything is 
looking good so far. I still need to work out how we're going to collapse it
all back down into a graph at the end though... Like once the recursion 
bottoms out and you know there's not going to be any more splits, you need to
have a way to grab all the information from the local stack of each function
as you wind back up. I guess that's basically how we'd do it, since the call
stack should kind of just be linear since we're doing this weird BFS type 
thing.

Tomorrow I need to:
    - figure out why it's infinitely looping
    - maybe make it so we cluster the groups based on which parent groups they
      descend from. That way, we can rectify splits straight away?
    - write the splitting code
    - write code to repeat the process with the next level in BFS
    - write code that builds a full graph while unwinding once we hit the 
      bottom
    - Once we've got the graph, repeat the whole thing over the new graph, 
      and keep repeating until the graph is a tree.
    - ... profit?

gn :)

--- the next day ---

Ok, so the infite loop thing was easy.

As to clustering groups based on which parents they descend from, it shouldn't
be too difficult, but the code will probably be nasty... let's go

Done...

--- the next day ---

So I got that todo list mostly done yesterday, but I now see that ther's a 
slight issue with it, it seems as if the same node was appearing multiple 
time in the child groups...

Turns out it was just a bug, needed to check if it had already been identified
during 1.1 before adding it to the cluster thingy.

Anyways that seems to be fixed, so back to building up the graph :)

...

Ok, so we're getting something rendering but it looks a little... different?
Seems like things aren't connecting up with each other very well...

Well, with a bunch of fiddling, I've gotten it to generate the next level of 
the graph :)

Now the other day I was thinking about repeating the process. Before I'd said
that we would repeat until the graph we were left with was a tree, but on 
reflection I realise that doesn't make sense. Instead we will continue until
the number of nodes in the new graph is equal to the number in the old graph.


IT WORKS!!!!!!!!!!!!!!!!!!

--- like a week passes... ---

Ok, where were we??? 

Let's try to understand why the C nodes weren't getting merged at the same 
time as the B nodes. That seems like a bug which could lead to incorrect 
conversions to occur in some cases.

The issue is that since we cluster the nodes based on their parents, and the C
nodes actually don't share parents, so they won't be merged at that stage. So
what we need to do is check whether the parents of the C nodes are all 
considered compatible. So this means that if all parents of node C1 are in a 
member of the higher_lvl_sec, and all the parents of node C2 are in another, 
different member of higher_lvl_sec, then we know they're compatible. Otherwise
I guess they're not...? And you might need to split...?


Hmm... I've drawn out a new query (querytest23) to help think about this, and
it's looking like the end result of this conversion may not be a tree at all,
but rather a directed acyclic graph. I'm not sure how I feel about that. Also,
when I run my existing code on that query it's very broken. Like some nodes 
completely disappear... so yeah, definitely some work to be done here still.

Let's start by trying to resolve this issue with the clustering. I think that 
as a first step, we'll be more lenient in how we merge children based on their
parents. In the current version, the children need to have the exact same set
of parents. In the new version, we'll allow them to be merged so long as all 
parents of child1 correspond to parents of child2 in the same higher 
level SEC which we received as an argument to the function. Sounds confusing, 
might be easier to just write the code lol.

I suppose we also need to decide what to do if the children *don't* turn out 
to descend from parents in the same higher level SECs. Actually I don't think
that even makes sense... Let's just try writing some code and see what 
happens.

--- next day ---

Ok, well I managed to get that working last night and it looks perfect on 
QT18. However on QT23 it's breaking, so there's something wrong. For some 
reason it seems like the `seen` mapping isn't being populated the way I'd
expect.

Ok, it turns out the issue was that keys in the dictionary weren't unique, 
which I found out kind of accidentally by changing them so they were unique.
This makes me slightly concerned that this might still be a bug which would
show up in non-synthetic query graphs. At some point I should try to change 
the clusters dictionary so that the key is properly unique.

At this point I'm also pretty confident that our SECTree will actually be an
SECDAG. Gonna need a better name for that I think.

Ok, things seem to be going quite well anyways, so at this point I'm going to
start working on the splitting code. We've made a quick change to check if a
split is necessary but I'm not sure if it's working. To test that I'll create 
QT24 which will hopefully exhibit splitting behaviour.

--- next day? ---

So yeah, QT24 indicates that our detection on when to split is way off. It 
needs to be based on the higher_lvl_secs that get passed from the caller. If
the groups at current level exceed what we'd expect it indicates that we 
*might* need to jump back to a higher level and fix things. Just need to nail
down the exact details of when we should / shouldn't backtrack. Basically we
need to work out which of the high lvl secs are incorrect, if any.

--- ... ---

Ok, so I had worked through that example to understand when the splitting 
needs to occur, and how. I've got a better idea of how to do it now, so let's
write the code.

Well, after a bunch of fiddling, it seems quite close but for some reason it's
crashing after the alg completes, when it tries to render the graph...

Ok so... it seems like somehow the higher_lvl_secs is ending up having entries
without any members. That's obviously invalid though. Interestingly it seems 
to be happening for the 'a' node too, which is at the top. I've got no clue 
why that would happen though, the backtracking should never get that far, so I
don't really see how adding the backtracking in could have broken it...

I've added some assertions when constructing SEC objects, and there's 
definitely always members at construction, so I must have inadvertently 
modified the object.

IT WORKS!!! I was modifying the members array when doing my split checks, but 
I forgot that this would persist even in circumstances when a split *isn't*
needed, hence the graph was being messed up. So instead, I made a quick copy 
of the members array, and worked with that during the split checks.

IT WORKS!!! IT WORKS!!! ABSOLUTELY BUZZING :) :) :) :) :D :P

--- next day ---

Ok, at this point I suppose I should maybe tidy up the code a bit. There's 
various ways it can be refactored to reduce duplication, and increase clarity,
so let's do that.

Well, I've rearranged it a bit, and it could probably be improved further, but
to be honest, I kind of want to keep progressing. I think I'll work on making 
the visualisation of the final DAG more rich. Need to include the number of 
replications, and include data about the original node ids.

Ok, I've worked on the visualisation somewhat, and it's certainly a lot 
better. That being said, I'm noticing that we might be losing some important
context with our current datastructures. In the visualisation of QT18, we can
see that the replication boxes for 'b' and 'c' are separate, which one might 
take to mean that these can be permuted independently without creating invalid
matchings. However that is not the case. The 'c' nodes in the original query
graph must descend from particular 'b' nodes at the parent level. I'll need to
investigate tomorrow to see if this is simply poor visualisation on my part,
or if the actual results of the conversion need modified.

It's also worth noting that, when we look at the step by step output during
conversion, it seems like this information is at least available, so we should
be ok, even if it does come down to modifying the conversion algorithm.

We can see the same problem with QT23, but QT24 looks perfect.

Another thing I need to look at is making the labelling of the clusters have a
correct label indicating whether the nodes are connected. Currently this is 
hard coded, so obviously wrong. Actually, this makes me think, if you have 
several generations of node groups in the same replication cluster, is it 
possible for one of those groups to be replicated but the others not? If so, 
we'll need to think of a better way to indicate that a node group is 
connected. Perhaps that information should actually be in the label of the 
node that gets rendered? But actually that would get confusing, since the 
replication won't necessarily only happen at the lowest level. Perhaps I 
should think more about what sort of graphs would exhibit connectedness at
higher levels of the conversion proces...

Anyways, that's enough for one night.

...

Ok we all know that's not true... just can't stop thinking about this. I'm 
trying to dream up a possible QT25 which would exhibit higher levels of 
connectedness. I'm coming up against some pretty fundamental questions. So in
our current conversion process, the initial `sec_graph` that gets passed in is
generated by building a new graph from the query graph, simply mapping nodes 
in the query to SEC nodes which have a single member (id of the query node), 
and the same label as the node. We then add all the same edges from the query
back into the sec graph. However this creates a strange situation, since the
sec_graphs that we actually generate could never have edges between sibling
nodes. However since the query graph is just a regular graph, it means that 
the top level call to `combine_structures` could have an `sec_graph` that 
violates this invariant. 

Now I'm wondering how to handle this. Wiping these excess edges out of the 
`sec_graph` seems like it wouldn't be valid, since it would imply that certain
nodes might be symmetric when in fact they're not, due to inter connections 
which are no longer visible (under this course of action the idea of 
'connectness' of nodes in an SEC would never arise). 

Another possible course of action would be to allow such sibling edges. In 
this case, we have to ask whether the `sec_graph` which is returned from 
`combine_structures` *should* be allowed to insert sibling edges. The question
is when you would want to do this. The possible QT25 that I've dreamed up 
seems like it would exhibit a good example of when you'd want such behaviour.
At the lowest level we have a number of clusters which got separated due to 
their having differing degrees, and not being fully connected. However, there
does still exist edges between these groups, so we could perhaps allow the 
resultant `sec_graph` to have such edges inserted? This would result in a 
situation where higher levels of connectedness *would* be possible. I think 
the real test for this will be to think about a matching, and to manually 
consider whether all permutations of that matching would be valid under the
higher level connectedness. If so, then I guess it stays :).

I really hope we can work this out in favour of having higher levels of 
connectedness, since that would presumably lead to the most possible 
permutations per matching.

--- next day ---

Ok, today I want to think about connectedness, and how it would work at higher
levels in the `sec_graph`. I've drawn up QT26, which perhaps is a bit simpler
than QT25, and also elicits some interesting questions about how our algorithm
is *really* supposed to behave.

Ok then, QT26 *definitely* indicates that there's some issues with our current
approach, and reasoning about, connectedness. Currently it merges all the 'b'
nodes into a single SEC node, which isn't correct. I think we need to add a 
rule which states that if any SEC in a grouping was constructed out of 
connected members, then all must be. Also we presumably need to have a rule 
that all members of a grouping must have SEC's with the same number of members
themselves? I'm not exactly certain on how that works out but yeah...

I think that the way to resolve this is to maybe think about how we'd go about
making use of this datastructure during the query phase. Like how do we work 
out how many matching permutations a `sec_graph` has, and what exactly are 
those permutations.

Ok, I'm thinking that higher level connections *should* be allowed. I think 
that once the groupings at a particular level have been fully developed, (so 
after the backtracking), we look through each of our new SECs. For each one we
add an edge between it and any other of the new SECs if all members of both 
SECs are fully connected to each other. The labels don't matter I think?? The
edges that we insert should be bidirectional.

Yeah... I think these extra edges will be pretty essential for working out the
set of permutations for a given matching. Let's maybe work through that a bit
now.

I think I'll try coding up these new rules that we're thinking about. Also 
need to make it so the visualisations will be able to represent these extra
edges somehow. I think we'll try to make them visually distinct, since they
carry a somewhat different meaning from the edges between levels in the graph.

Ok, so I've updated things. Now every SEC has a field `is_connected` which 
indicates if its members form a clique. I've updated the visualisation to also
reflect this, by adding the connectedness to the label, however this clearly
isn't correct. It should really be an attribute for each subgraph. The problem
is that graphviz creates quite a big distinction between subgraphs and nodes. 
In my usecase it would be very useful to be able to have nodes that contain 
other nodes, but we can't, so I'm having to pretend that subgraphs are nodes.
That seems to be breaking down quite quickly however, and it's a bit visually
confusing anyways. I'm not really sure what I can do about it though...

I might want to investigate other forms of visualisation, but graphviz is 
actually really good and easy to use. I don't want to have to use anything
that would require me to do my own layout.

--- several days later ---

Well, after a hectic few days with work, we are back.

Um, glancing over the previous work I was considering, I mentioned that the 
edges between higher level connected SECs should be bidirectional. However, as
I think about it, we probably don't actually need any directedness in our 
graph at all. The idea is that we're doing a BFS starting from a given node, 
and so we don't really care about the direction of edges. So yeah, when we add
edges between sibling SECs, that's all they are. Edges.

Ok, well I've implemented a rule that forces all members of a group to have 
the same `is_connected` attribute, which helps improve some things. I also had
a go at improving the visualisation a bit. All the edges are undirected now, 
and it should show connections between siblings, where they exist. I also 
tried to make it so that nodes which are at the same depth in the BFS are at
the same rank, but it seems like this might not be super easy with graphviz, 
at least not without modifying it heavily. That's ok though, since it is at 
least visualising things correctly with the correct clustering as-is.

Ok, I've added the code to join siblings together, and it seem to be working. 
I'll maybe try adding our QT25, and see how the output for it looks to check.
Of course, I don't actually know what the output is *supposed* to look like, 
so I'll need to think that through also.

Well, it doesn't work. At least, I don't think it does. Still not exactly 
clear as to whether it should be adding the sibling edges on the particular
example. Regardless, it definitely is messing up by trying to merge everything
into a single node. Not sure why it's doing that, so we'll need to add a new
rule to ensure it doesn't try to merge those things.

I *think* that we maybe just add an edge if *any* members of the 
`higher_lvl_sec`s are connected? Perhaps there's some edge case where that 
will lead to incorrect conversions, but we'll just see I guess.

Hmmm.... that's led to a *very* strange final result for QT25.

Ok, turns out it was just a bug with my visualisation -- fixed. Output now 
looks exactly how I was hoping which is awesome. At this point I think I just
need to start testing a lot, and trying to find any issues with what I've got
currently.

That's all I'm gonna do tonight. Some things I should maybe think about:
 - In our visualisation, the connected information needs printed on the 
   subgraphs
 - We also need to add information about the query graph node mapping into the
   visualisation, so it's clear how to get back to the query graph
 - I should maybe think about whether this conversion algorithm will turn out 
   to be bijective i.e. could we get back to the query graph from the SEC
   graph. If the answer is yes, then that could open some interesting options
   for how we actually want to do our matching... or maybe not. We'll see.
 - Finally, we just need to create a bunch of test queries, and verify that 
   the output is what we want. We should look into automating that if possible
   too, although that will require me to nail down exactly the object 
   representation that we want for the final SEC graph.

--- next day ---

Ok, I suppose I'll make a few more test queries now.

I've drafted QT27, which is basically a single layer of 5 children beneath the
start node, connected as a path, and they all descend from the start node. 
This graph is definitely producing an incorrect result that needs 
investigated.

I think I need to work on getting the nodes marked into our visualisation.

Ok, I've added some code in to show us the mapping back to query nodes in the 
visualisation. Looking at QT27, it actually seems as if it could be correct.
It certainly seems as if QT27 is opening up a lot of interesting thoughts. It
seems that this conversion process might not be deterministic i.e. the order 
in which nodes are evaluated will affect the structure of the resulting graph.
This is definitely not desirable. I might have to tweak the rules somehow to
make it so that it behaves in a predictable way... I think the nondeterminism
here is probably arising from my algorithm simply not being complete, or 
having some incorrect assumptions encoded into my rules.

One possible issue with QT27 is that after grouping nodes {2,7}, which seems
correct to me, it decides to also group {3,4}. I can see why this happens, 
since this proposed group perfectly fits my rules, and there isn't any child
nodes that would split it apart. The problem is, firstly, if this grouping 
*is* valid, it raises the question about why grouping {4, 5} wasn't picked 
instead. The result would be completely arbitrary, and having such a 
nondeterministic algorithm feels wrong to me, for such a precise process. 

So, the only conclusion is that the grouping {3,4} (and likewise {4,5}) 
*isn't* valid. I can think of a few reasons that we might argue this. First of
all, we can see that there is a sibling edge between 3 and 2, but there 
*isn't* such an edge between 4 and 6. This is a somewhat asymmetric situation, 
and I think it indicates that these nodes aren't compatible.

So, we need to craft a rule to deal with this situation, so let's get precise.
I think the basic rule is that all nodes in a group must have the same number
of edges to another group. So if a member of group A has 3 edges to nodes in 
group B, all nodes in A must have 3 edges to nodes in group B? I'm not exactly
sure if it matters *which* nodes. Presumably since the rule gets applied in 
both directions, it would work itself out... somehow?

The interesting thing with the above rule, is that (I think) it requires all
the groups to have been formed to the best of our ability already, i.e the 
other rules have all been applied. Then, once that's happened, we'd need to
have a loop that keeps trying to split the groups up based on this rule until
it stabilises.

*Another* interesting thing with this rule is that I think we'd need to run it
again after we call `combine_structures`, if the returned split groupings have
changed from the proposed groupings. If a split has occurred, it could have 
broken the balance, so we'd need to run the rule again to ensure that things
can be stabilised. So yeah, it's going to be complicated I think.

Hmm... for the record, I don't think any of my rules that care about multiple
groups have considered the groups descending from other parents. Not sure if 
it matters, but gonna write it down so I remember -- Ok, I've glanced through
the rules, and I don't think this would affect any of them :)

However, the above issue definitely *does* apply to my new rule.

Random thought -- unit tests would be *very* useful for a lot of this code. I
should maybe try to create test for each of the different rules, since they 
are nicely logically separated things we can work with. At this point the 
larger structure of the algorithm seems quite stable, so it should hopefully
be quite doable.

--- next day ---

Ok, let's continue with adding that new rule.

Actually, taking a step back and looking at QT27, I think I'm a bit off with 
it. It seems to me like there's two permutations of the B nodes for any valid
matching. Firstly, there is {2,3,4,5,6}, and secondly, {6,5,4,3,2}. No other
permutations exist that I can think of. Yesterday I was assuming for some 
reason that there was going to be more symmetric groupings to find, but I 
don't really think there is to be honest...

I think the rule I proposed yesterday is basically correct but I think the 
important detail is maybe that it should actually run as one of the first 
rules, rather than after other rules. 

Well... I guess my uncertainty right now is that I'm not sure my current 
algorithm knows how to deal with the symmetry seen in QT27. Like I don't think
any of my rules lead to an SEC graph that would be able to exploit this 
symmetry. Obviously, I want to be able to maximise the amount of symmetric 
regions that can be recognised. Indeed I think it should be possible to 
recognise *all* types of symmetric regions in a graph, with the right 
algorithm.

I'm thinking that we can make use of the sibling connections to make this work
sort of. Essentially, once the conversion has completed, when we're working 
out valid permutations, we have to ensure that all permutations would respect
the sibling connections. In the case of QT27, this would mean that the fully
converted graph would look like the initial query graph. When checking for
permutations, it would know that just swapping nodes 3 and 5 for example, 
wouldn't produce a valid permutation, since 3 has an edge with 2, but 5 
doesn't, and likewise 3 doesn't have an edge with 6, while 5 does. That's just
one example, but I think it should make it somewhat clear. 

So, the problem now is we need to figure out a good rule for ensuring that the
final result for QT27 results in no change being made. I guess that this rule
actually derives from the stuff we were talking about before. In essence, all
nodes in a group must have edges to the same set of sibling nodes outside of
that group. 

--- next day ---

Ok then... let's do it I guess.

So, it turns out it wasn't too difficult, and the rule was able to be 
implemented in the same fashion as the existing rules. I did add a higher 
level variable to track some things that made it a bit easier, but overall not
too bad. The rule appears to work perfectly, and converts all previous queries
correctly also, which is good.

So, at this point we're back to the position where everything *seems* to be 
correct, although I've been here before. I need to continue designing test
cases to work through, and try to unearth weird edge cases. 

--- next day ---

I think at this point, I'm going to look through all the other existing test 
cases which I copied over from the original project. Let's keep a record here:

QT1:  Simple case that would impossible to get wrong (ha)
QT2:  More complex graph. Conversion currently looks INCORRECT
QT3:  Simple 3 node graph. Correct
QT4:  I think this was an example data graph from TurboISO. Input maybe 
  incorrect.
QT5:  Correct
QT6:  Correct
QT7:  Very similar to QT6, just one node different. Correct
QT8:  More complex example, lots of different B groups. Correct
QT9:  Causes program to throw exception? INCORRECT
QT10: Correct. Had to draw it out tho
QT11: Also drawn out, correct.
QT12: Correct
QT13: Correct
QT14: Trivial, correct
QT15: Similar to above, correct
QT16: No change, correct
QT17: Correct, although highlights need for better visualisation 
QT18: One of our main tests. Correct
QT19: Correct, same visualisation issues though
QT20: No change made, correct
QT21: Correct
QT22: INCORRECT, issue arises during intermediate step it seems.
QT23: Another main test, correct
QT24: Same as above, correct
QT25: As above, correct
QT26: Another correct of our most recent tests
QT27: Final test, correct.

Ok then, well I'm pretty happy with how that went. Almost all the graphs had a
correct result. I think we'll start by looking at the most egregious error, 
which has to be the exception thrown by QT9.

Aside:
I've just done a bit of googling for prior work, and the term "automorphic 
equivalence" has come across my radar. Based on what I see on wikipedia, it 
seems the term isn't directly relevant to the work I'm doing, but is closely 
related. The wikipedia page (https://en.wikipedia.org/wiki/Similarity_(network_science)#Automorphic_equivalence)
also discusses Structural Equivalence. This term clearly has a different 
meaning from the Structural Equivalence Class discussed in my own research, 
and as such I will *definitely* have to think of a different name. However, I
think we are certainly dealing with a type of equivalence, since all the
definitions on that page feel quite close to what I'm trying to achieve. 
Perhaps something like "Strict Automorphic Equivalence", to make it clear that
we *do* care about the label of the node. That being said, I might be wrong 
about the definition of Automorphic Equivalence, it depends what precisely 
they mean when talking about the "label" of the nodes. Normally the same label
could be seen on multiple nodes, but we don't see that on the examples on that
page. For now I'll hold judgement, and come back to it later.

Hmmm... I've put in a potential fix for QT9, and it now runs. However, the 
result looks quite wrong. Going to need to check that things haven't regressed
elsewhere.

Ok, my main tests look ok at least. At some point I'll rerun everything, 
ideally set it up as automated as I can, checking things by hand is very 
uncool. Probably can't automate until the datastructures stop fluctuating so 
much.

Ok, so QT4 did indeed have a mistake in the input file. After fixing it 
however, the converted graph looks incorrect. The result really is quite off.
I'll have a look at the other graphs with issues to see what's up with them, 
and try to find a common theme.

QT2 still looks wrong. All the B's get merged at once which they shouldn't. 
QT22 looks like it's having a similar issue to QT9. I think QT2 could be 
something separate, and it's probably easier to identify, so I'll look at it
first.

Hmm... it feels weird, but I'm thinking the rule we added the other day that
sibling connections must be to the same set of nodes for all members of a
group, should actually be extended so that it's not just about sibling nodes,
but also about child nodes? It will possibly reduce the effectiveness of the
conversion though, since it wouldn't be able to optimistically group things...

I feel like, up until now we haven't *actually* been merging larger sections 
in a way that would let us truly see the symmetry in a graph. The handpicked
test cases look decent once converted, but the problem is that our 
"replications" are still on the level of individual nodes, rather than on 
structural subsections of the graph. I thought for a while that I'd be able to
figure out that information from the graph we were building up, but now I'm
not so sure. I'm starting to think that we need to rethink how we're doing 
things to allow large sections which are made up of multiple generations in 
the BFS to be merged into a single unit.

Perhaps what we do is similar to currently:

  - optimistically merge all the nodes at a given layer into a single 
    structure
  - apply rules similar to what we currently have, which split things out into
    a smaller number of structures
  - once the structures have been found, we identify which parent structures 
    that new child structure is inheriting from
  - if a child structure inherits from just a single parent structure, then we
    merge it into that parent structure (? maybe only when the recursion is 
    done successfully)
  - if a child inherits from multiple parent structures, then it needs to be 
    in a higher level structure. We backtrack at this point maybe??
  - If backtracking occurs, it might mean that structures need to be broken 
    apart so we can try again

The above process is very similar to what I have currently. I think the main
difference is that we need to actually add child nodes into the same 
structures as the parent nodes after the recursion has completed. Within those
structures we still need to maintain edge information, so that when the 
algorithm is repeated at a higher level, it's able to accurately assess 
whether two nodes are equivalent.

It's a bit annoying to have to do this, since it's a pretty drastic change, 
but I think what I have currently just isn't correct, so I suppose a change is
needed.

--- next day ---

Ok, I think this refactor is going to be pretty extensive. I think the easiest
way of doing things *might* be to actually have the structural nesting done as
a separate thing from the graph. So the graph would indicate which nodes are 
connected to which other nodes, but the structures would indicate how sets of 
nodes are composed.

So umm... how do we actually do that?

I've drawn out a few test cases, QT28-30. They demonstrate some interesting 
behaviour, and I've worked through the step by step conversion for them, and 
found it quite helpful. QT30 in particular makes me think that nodes with 
different labels will need to be able to be put into the same groups. I'm
starting to think the only rule which will apply to nodes is that they have 
the same set of neighbours (with the exception made for nodes connected to 
each other). If this is the case it could prove to be quite nice.

--- several day later ---

Ok, feeling a bit healthier, so let's get back into this.

I'm thinking the way we want to do this change is as follows. The final data
structure will be made up of a graph and a tree. The graph will basically have
the same structure as the query graph, but with the replications taken out. 
The tree will contain the replication units, showing how they compose. Each
replication unit will either contain other replication units, or at the bottom
level they may contain a single node, which maps back to the original query 
graph.

I'm not really sure that systems quite going to work though. We really need 
each replication unit to be somewhat aware of how it connects to the outside
world. Consider QT30, during it's second simplification call. It's needing to
merge the 'b' and 'c' nodes in each of the replication units. To do this it 
needs to fully understand what other nodes they are connected to. This is 
kind of tricky though. Since those nodes could actually exist several layers
down inside a number of replication units. We don't care about edges for these
nodes unless they cross the 'border' for a particular replication unit. So I 
guess we need a way to lookup edges the start inside a replication unit, and 
end outside of it. That's somewhat complicated I think. 

Hmmm, I suppose it might be useful to consider what the highest common 
replication unit is for a given edge. Like the lowest common denominator for 
the two nodes. I think that, typically, that's going to be the thing we care 
about when trying to merge things?

 We also need to think about how we're going to compare the internal structure
 of replication units. Basically to be able to merge, they will need to have 
 isomorphic internal structures, and also be connected to the exact same set 
 of external nodes. Also that internal isomorphism must also account for the
 replications. I suppose one way to check that would be to get a list of all
 original query nodes for each replication, and make a subgraph of the query
 graph including only those nodes. If it's isomorphic between the replication
 units then it's good.

--- next day ---

Well I've done a bunch of thinking about how to represent this datastructure
in a way that's useful for the things we need to be able to do with it.

I'm thinking that we may be able to represent everything in one big graph 
after all, and to be able to do so *without* encapsulating subgraphs. It might
still be useful to think in terms of encapsulations, but let's see how this
looks.

--- like two weeks later ---

Ok, I've taken some time to do other stuff and now I'm back. I really want to
tackle this datastructure decision once and for all, and then get it 
implemented, so here's how it's going to go.

We're going to have a class `ReplicationGraph`. This is going to contain both 
a graph representation of the nodes, and also a tree for the nesting of our
`ReplicationUnit` class. This class will contain a list of all the nodes it 
contains at the top level, as well as another list of all the 
`ReplicationUnit`s that it contains.

I think the `ReplicationGraph` will also need to include a mapping from the 
RGNodes back to the original query nodes. This will be a one to many mapping.
It might also be useful to store a separate mapping from edge pairs back to a
"lowest common denominator". This LCD would be the deepest RU which 
encapsulates both nodes from the edge. This information should be useful to 
have cached. However, I think this is basically just an optimisation, so it's
probably not actually necessary.

Let's get started.

Ok. It seems to me that our `ReplicationUnit` is going to want to have a 
precise, deterministic ordering of it's contained items, both children and 
nodes. This will enable us to efficiently compare two units to check if they 
are equivalent. I think for now we'll order by... actually  maybe it's not
possible to determine such an ordering? Like if we consider a clique, all the
nodes are equivalent, so there'd not really be a way to figure out the correct
ordering. Of course, in the case of clique that's fine, but in other graphs it
might be more annoying. There's definitely ways to do it properly but it's 
just going to be a massive pain, I can tell already.

Well I suppose that the ordering of RNodes is pretty straightforward. For them
we can just do the ordering based on which query nodes they map to. Basically
just order based on the lowest ID of query nodes that a given RNode maps to.
Since any QNode can only be pointed to be a single RNode, we know there won't
be any conflicts.

As to ordering contained RUs... well, I suppose we could just skip that if we
were able to come up with some sort of "hash" for the RU. I think that if we
kept a cache of all nodes that exist within a RU, you could use that to 
quickly build a subgraph of the query graph. When comparing RUs all you'd need
to do would be check if their respective query subgraphs are isomorphic. Seems
kind of crazy but I guess it'd work?

And if we did that, then we probably wouldn't even need to think about 
ordering the GNodes either. Not that it's especially difficult, but still.

I think that if the two subgraphs *are* considered isomorphic we'd also need 
to ensure that the nodes also all had the same degrees in the context of the
full query graph, since that would affect things... I think?

Ok, so I've got the test passing. It seems as if it's kind of working?

--- another two weeks go bye... ---

Ok, it's been a while. I guess motivation can be tough sometimes. Anyway, I'm
back, and ready to get back on it, so where were we?

Ok, I've been starting to work on the merging process and had a slight idea.
When we're trying to combine RUs I guess there's two ways that can happen. In
one instance, the two would actually get merged such that the new RU accounts
for both. So essentially you would get something with replications > 1. This
would occur when labels are the same etc. In the other case, you have a pair
of RUs which are compatible in that their sets of neighbours are equal, but 
they themselves aren't exactly equal. In this case, it's sufficient to simply
place them both into an RU with replications=1. This seems to make sense, but
I'll give it some more thought to see if there is further nuance.

The other thing is that we need a way for child RUs to get pulled up into the
parent RU under certain circumstances. We will do this when the child RU has 
only get edges going into the parent RU. Or maybe require that it only has a
single outgoing edge (which by definition would go to the parent). Need to 
figure out which of those is correct... I think the former, QT30 itself 
illustrates that you might have multiple edges flowing to the parent, but it 
is still valid to merge in.

Ok, so I've gone through QT30 in a bunch more detail and it's giving me some
insights. I'm realising now that the initial conversion from query graph to
replication graph doesn't need to wrap the entire thing into a single RU. The
reason being that after the full simplification has occurred, the entire graph
will end up being wrapped in a single x1 RU. But during the simplification
process this could throw up some issues. Reason being that we wouldn't be able
to find the lowest common ancestor. I suspect this might not actually be an 
issue as I'm not sure if we actually need to do that. We would never be 
dealing with RUs other than the top level ones, which therefore won't have an
ancestor.

Anyways, when merging siblings, we need to prioritise merging of isomorphic 
RUs before those that merely have matching neighbour sets.

--- next day ---

Last night I think we finished identifying the child nodes. So today, lets 
make a start on the merging process.

Ok I actually ended up quickly rewriting the logic for the building of 
children. It's a bit cleaner now and I've got a lookup thing.

--- ... ---

Well the hayfever has me good, but lets try to get something done anyways.

Made a little progress, but I think I might have to change approach a bit.

--- Couple days later ---

Umm yeah I think we need to modify way we're approaching splitting maybe.
Well, reading the split checking code from the previous version... wow I have
no idea what that's doing. Let's make sure to document things better this time
around.

Slightly off topic, but did some googling there. The term "automorphism" seems
to be extremely relevant to the work I'm doing here. In particular it leads to
this page on "Symmetry groups" (https://en.wikipedia.org/wiki/Symmetry_group).
The description seems to capture the essence of what I'm doing really well:
    "the symmetry group of a geometric object is the group of all 
     transformations under which the object is invariant"
Now tell me that's not interesting.

Anyways, now I'm tempted to just spend the night reading wikipedia and 
learning about group theory to see if there's any relevancy there too...

Hmm, it seems that graph automorphisms are interesting, but I think that they 
are actually more closely related to the original TurboISO work than to what
I'm doing. With these graph automorphisms as described here: https://faculty.etsu.edu/gardnerr/4127/algebra-club/auto-talk.pdf
it seems that nodes are only swappable if they will have precisely the same 
set of neighbours after the sway, which is essentially what was described by
the Neighbourhood Equivalence Class in TurboISO. 

However maybe I'm slightly off here - the above presentation shows that an
automorphism isn't made up of just a single swapping of nodes, but rather a
mapping of nodes from V(G) -> V(G'). So multiple swaps are being made at once,
and the result is considered automorphic if and only if all nodes still 
precisely the same set of neighbours as they did before the mapping...

Hmm, yes I actually think that this perfectly describes what it is that I'm 
doing...

So I wonder if there's any algorithms out there for this already. It would be
interesting to see if I could even just take existing code...

Perhaps one difference with the Graph automorphism problem is that it doesn't
work outwards from some starting node... Well, it certainly makes it slightly
different, although I don't know if having a specific starting node would ever
*increase* the possible automorphisms, I think it would only restrict it.

I mean, perhaps this will allow us to broaden our horizons more... Like what 
would happen if we just made use of the full automorphism group and said that 
there's that many results for every valid matching found... would that be 
valid?

Actually yeah, you 100% could, the only thing is that you'd have to be careful
that you don't double count a result by coming from some other angle. So for
example if your start node is itself swapped by an automorphism, you have to
be aware of the data graph node that it's being mapped to. If another matching
is found starting from that node, you'd need to be careful to ensure it's not
the same one that was already found. 

How to do this? Well one option might just be to disallow automorphisms that
involve swapping the start node, but that seems like it could (in theory) 
block a large number of valid automorphisms (in the degenerative case, 
granted). Another option would be to somehow track the full set of data graph
nodes used in the result, and require that no other result is allowed to use 
precisely that set of nodes (since it's guaranteed to have been covered by an
automorphism of an earlier matching). However, tracking these sets would 
basically be impossible, right? Like there it would use an insane amount of 
RAM plus it would be very slow to look up.

Perhaps the problem could be dealt with by saying that, when we encounter an
automorphism that swaps the start node, we must immediately do an exploration
from that swapped data node? *ACTUALLY*, what we could do is actually delete 
the edge between those swapped nodes.... or could we... maybe not actually.
Well perhaps a related idea is that after fully exploring a candidate region,
and extracting all the results, you simply delete that starting node from the
graph.

But I suppose this would break certain things. Like for example if you're 
wanting to do parallel processing it could be weird. Plus it would require you
to essentially just explore a single candidate region at a time, since you'd
potentially have problems where the start node for a region is itself 
contained within another region.

Perhaps there is a way that the start node could be guaranteed to never 
intersect with another candidate region, we could perhaps just make it that 
when identifying candidate regions, this is one of the rules you have to 
confirm.

--- several days later ---

Ok, I haven't done any coding for this recently, but I've done a lot of 
thinking, and a lot of research. I've spent some time trying to understand
basic group theory, and the properties of a graph's automorphism group. It 
seems like this idea is really promising and could be very useful for solving
these problems. 

I've downloaded a program called Conauto which claims to be able to compute 
the automorphism group for graphs presented in the DIMACS format, so I'm going
to convert a few of our querygraphs and have a look at them using this 
program.

Interestingly, in the process of looking more closely at QT23, it seems that 
the process I had been pursuing would have at least needed some modifications
to actually be able to recognise the full symmetry of the graph. Anyways, it 
seems to me upon a manual inspection that `|Aut(qt23)| = 8`. Conauto on the 
other hand is saying it's 2... It also is talking about orbtis and other stuff
too though so I need to look into it more.

--- two days later ---

Well I figured out the issue with conauto -- it assumes that the input graphs
are directed. When I added extra edges to the input, everything started 
working beautifully. For QT23 it computes 8 automorphisms, which is exactly
what we expected. Excellent.

--- the next day (?) ---

Had a go wrapping conauto with Rust bindings, seems to be going ok. At some 
point I'll add that stuff to this repo.

--- next day ---

Ok, let's continue on those bindings. I think I'll maybe be ditching the 
Python stuff for now, since I don't want to also create bindings into python,
which would also involve integrating with Networkx somehow, which isn't fun.

Instead, I think I'll just write my algorithm in Rust. I also think that the
algorithm might end up being just a variation of the Ullman algorithm, so 
that should be a good place to start. I think I already have a Rust 
implementation of it too, which is great.