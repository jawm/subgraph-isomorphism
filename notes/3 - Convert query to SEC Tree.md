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