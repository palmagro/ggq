## Graph Pattern Matching and Multi-Relational Decision Tree Learning in Graph Databases

"Induction allows automatic construction of classification trees from a set of previously classified examples. Normally, algorithms that build decision trees through induction are limited to those working with flat data: a fixed set of objects and their attributes. These types of algorithms don’t take into account other objects attributes even though they are directly connected to them and can provide valuable information. Machine learning technologies capable to take into account other objects attributes with which the studied object interact are grouped into Relational Machine Learning  (Multi-Relational if different types of relationships are taken into account). These technologies have been an emerging research area in recent years. Specifically, algorithms like MRDTL [1] (Multi-Relational Decision Tree Learning) which allow to automatically build multi-relational decision trees from records immersed in a relational database. However, finding relational patterns in these types of databases implies a great deal of expensive JOIN operations between tables. Despite their name, relational databases do not physically store relationships between records, making them unsuitable for this type of task.
 
We have implemented our own multi-relational decision tree learning algorithm. This implementation has been developed in Python and is able to automatically induce trees from structures (subgraphs) stored in a Neo4j database. The algorithm (inspired by MRDTL and concepts like Graph Simulation and Regular Pattern Matching) use the concept of Generalized Graph Query (GGQ). A GGQ is a multi-relational pattern that acts as an attribute in the decision tree construction process. A structure immersed in Neo4j will take a true or false value for each GGQ (depending on whether it matches its pattern or not). Such GGQs are built dynamically during the tree construction process: the algorithm performs pattern mining all while learning a classification tree for the structures stored in Neo4j. This algorithm is more efficient, powerful and expressive than classic algorithms of this type that work on relational databases because the data is stored in a graph database." 

[1]: Héctor Ariel Leiva, Shashi Gadia, and Drena Dobbs. Mrdtl: A multi-relational decision tree learning algorithm. In Proceedings of the 13th International Conference on Inductive Logic Programming 2003, pages 38–56. Springer-Verlag, 2002.

We present two python libraries: **GGQ**, to perform graph pattern matching against a Neo4j DB and **GGQ-ID3**, to learn multi-relational decision trees from subgraphs stored in a neo4j DB. 

Next we we will demonstrate the power of both libraries, in the next eample we are using the Neo4j dataset named Minisocial (available in this repository to allow reproducibility). 

# Graph Pattern Matching

We will show how to use **GGQ** library first. Every element (node or link) in a GGQ have two flag attributes: "alpha" and "fixed". **alpha = true** (black color) means that this element in the GGQ **should be matched** at least with one node in the graph fulfilling his restrictions. **"alpha = false"** (red color) means that can not exists a element in the graph fulfilling the restrictions associated with that element in the GGQ. **fixed = true** means that the element in the GGQ should be matched with an element in the structure under analysis. **fixed = false** means that this element can match with any node/link in the graph fulfilling his restrictions.

We start by creating some GGQs...


```python
q1 = Ggq()
q1.addNode("a",True,"{}",True) #addNode(label,alpha,tetha,fixed)
q1.addNode("b",True,"{}",False)
q1.addLink(True,["a","b"],"",False) #addLink(alpha,gamma,tetha,fixed):

q2 = Ggq() 
q2.addNode("a",True,"{}",True)
q2.addNode("b",True,"{}",True)
q2.addNode("c",True,"{gender:'male'}",False)
q2.addLink(True,["a","b"],"",True)
q2.addLink(False,["a","c"],"",False)

q3 = Ggq()
q3.addNode("a",True,"{}",False)
q3.addNode("b",True,"{}",False)
q3.addNode("c",True,"{}",False)
q3.addNode("d",True,"{}",True)
q3.addLink(True,["a","b"],"",False)
q3.addLink(True,["a","c"],"",False)
q3.addLink(True,["b","d"],"",False)
q3.addLink(True,["c","d"],"",False)

q4 = Ggq()
q4.addNode("a",True,"{type:'photo'}",True)

q5 = Ggq()
q5.addNode("a",True,"{}",True)
q5.addNode("b",True,"{}",False)
q5.addLink(True,["a","b"],":wife]-({gender:'male'})-[:likes",False)

q6 = Ggq()
q6.addNode("a",True,"{}",True)
q6.addNode("b",True,"{}",False)
q6.addLink(True,["a","b"],"*..",False)

q7 = Ggq()
q7.addNode("a",True,"",True)
q7.addNode("b",True,"",False)
q7.addNode("c",False,"",False)
q7.addNode("d",False,"",True)
q7.addLink(False,["d","c"],"",False)
```

Next, we define some subgraphs in the Neo4j DB in order to test the Graph Pattern Matching algorithm...


```python
s1 = [6]
s2 = [5]
s3 = [12,13]
s4 = [2]
```

Creating Query System...


```python
qs = Qsystem(7474,"neo4j","******")
```

As an example, we evaluate if subgraph "s4" matches with GGQ "q7"...


```python
qs.query(q7,s4,[])
```

    True

# Multi-Relational Decision Tree Learning

Now, we demonstrate the power of the **GGQ-ID3** library. We should note that instead the formal work developed for GGQ allows to evaluate any substructure in a graph. The implementation presented here, still is under development, and can only evaluate and learn from structures consisting in only one node. 

As an example we will learn a decission tree able to classify nodes in the next tiny social graph:

![Toy Social Graph](https://preview.ibb.co/dQMut0/grafo1.png)

That graph represents some marital connections between users and information related to photographs publication. There are nodes of types user and photo, and edges of types wife, publish and likes. In addition, user nodes have gender property with value F (female) or M (male). photo nodes have None associated to gender property.

We will use GGQ-ID3 algorithm to construct the decision tree that correctly classify all nodes from Figure 2 according to their gender: M, F or None. First, we build a model, notice that the target field should be present in every node in the training set...

```python

modelo = Id3(7474,"neo4j","******","gender") #id3(port,neo4j_username,neo4j_password,target_field)
```

Creating a starting GGQ...


```python
q = Ggq()
```

Learning the decision tree from a training set of nodes...


```python
tree = modelo.execute_all_nodes(q,"user",5,50) #execute_all_nodes(initial ggq, type node, max tree depth, max nodes)
```

Then we can analyze the learned tree...


```python
tree.draw()
```

![Relational Decision Tree](https://preview.ibb.co/kOpdmL/social1.png)


As we can observe in the resulting decision tree, every node in the tree is associated with a GGQ that every structure that reach it should match.

A decision trees that to discriminate location types (Location,Hills, Forest, Valley, Mountain, Caves and Lake) in The Hobbit dataset (http://neo4j.com/graphgist/c43ade7d259a77fe49a8). A maximum depth of 5 levels was imposed in the construction of the tree, and some branches have been removed for presentation reasons:

![png](https://preview.ibb.co/nmqZRL/hobbit-tree-location-final.png)

Following GGQ allow to discriminate each character in a StarWars dataset (http://console.neo4j.org/?id=StarWars): according to whether it is devotee of the Empire, Rebellion or neither. They correspond to classification leafs of the decision tree automatically generated by GGQ-ID3. To construct it, nodes of type institution (along with the edges in which they participate) have been removed from the original graph database. The queries show that even working with small graphs a high semantic query level is obtained automatically.

#![png](https://s2.postimg.org/lxhg23vah/starwars-side.jpg)
![png](https://imgur.com/a/vfa8qSr)
[Imgur](https://i.imgur.com/77vmd3y.jpg)


