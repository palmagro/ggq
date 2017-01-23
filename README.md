## Graph Pattern Matching and Multi-Relational Decision Tree Learning in Neo4j

Induction allows automatic construction of classification trees from a set of previously classified examples. Normally, algorithms that build decision trees through induction are limited to those working with flat data: a fixed set of objects and their attributes. These types of algorithms don’t take into account other objects attributes even though they are directly connected to them and can provide valuable information. Machine learning technologies capable to take into account other objects attributes with which the studied object interact are grouped into Relational Machine Learning  (Multi-Relational if different types of relationships are taken into account). These technologies have been an emerging research area in recent years. Specifically, algorithms like MRDTL [1] (Multi-Relational Decision Tree Learning) which allow to automatically build multi-relational decision trees from records immersed in a relational database. However, finding relational patterns in these types of databases implies a great deal of expensive JOIN operations between tables. Despite their name, relational databases do not physically store relationships between records, making them unsuitable for this type of task.
 
We have implemented our own multi-relational decision tree learning algorithm. This implementation has been developed in Python and is able to automatically induce trees from structures (subgraphs) stored in a Neo4j database. The algorithm (inspired by MRDTL and concepts like Graph Simulation and Regular Pattern Matching) use the concept of Property Query Graph (PQG). A PQG is a multi-relational pattern that acts as an attribute in the decision tree construction process. A structure immersed in Neo4j will take a true or false value for each PQG (depending on whether it matches its pattern or not). Such PQGs are built dynamically during the tree construction process: the algorithm performs pattern mining all while learning a classification tree for the structures stored in Neo4j. This algorithm is more efficient, powerful and expressive than classic algorithms of this type that work on relational databases because the data is stored in a graph database. 

[1]: Héctor Ariel Leiva, Shashi Gadia, and Drena Dobbs. Mrdtl: A multi-relational decision tree learning algorithm. In Proceedings of the 13th International Conference on Inductive Logic Programming 2003, pages 38–56. Springer-Verlag, 2002.

We present two python libraries: **PQG**, to perform graph pattern matching against a Neo4j DB and **PQG-ID3**, to learn multi-relational decision trees from subgraphs stored in a neo4j DB. It uses the concept of "Property Query Graph" (PQG). A PQG is a multi-relational pattern and every structure immersed in Neo4j will take a true or false value for each PQG (depending on whether it matches its pattern or not).

Next we we will demonstrate the power of both libraries, in the next eample we are using the Neo4j dataset named Minisocial (available in this repository to allow reproducibility of this notebook). 

# Graph Pattern Matching

We will show how to use **PQG** library first, we start by creating some PQGs...


```python
q1 = Pqg()
q1.addNode("a",True,{},True) #addNode(label,alpha,tetha,fixed)
q1.addNode("b",True,{},False)
q1.addLink(True,["a","b"],"-[]->",False) #addLink(alpha,gamma,tetha,fixed):

q2 = Pqg() 
q2.addNode("a",True,{},True)
q2.addNode("b",True,{},True)
q2.addNode("c",False,{"gender":"male"},False)
q2.addLink(True,["a","b"],"-[]->",True)
q2.addLink(False,["a","c"],"-[]->",False)

q3 = Pqg()
q3.addNode("a",True,{},False)
q3.addNode("b",True,{},False)
q3.addNode("c",True,{},False)
q3.addNode("d",True,{},True)
q3.addLink(True,["a","b"],"-[]->",False)
q3.addLink(True,["a","c"],"-[]->",False)
q3.addLink(True,["b","d"],"-[]->",False)
q3.addLink(True,["c","d"],"-[]->",False)

q4 = Pqg()
q4.addNode("a",True,{"type":"photo"},True)

q5 = Pqg()
q5.addNode("a",True,{},True)
q5.addNode("b",True,{},False)
q5.addLink(True,["a","b"],"-[:wife]-({gender:'male'})-[:likes]->",False)

q6 = Pqg()
q6.addNode("a",True,{},True)
q6.addNode("b",True,{},False)
q6.addLink(True,["a","b"],"-[*..]->",False)
```

Next, we define some subgraphs in the Neo4j DB in order to test the Graph Pattern Matching algorithm...


```python
s1 = [5]
s2 = [4]
s3 = [11,12]
```

Creating Query System...


```python
qs = Qsystem(7474,"neo4j","pytpytpyt")
```

As an example, we evaluate if subgraph "s3" matches with PQG "q1"...


```python
qs.query(q6,s3)
```




    True



In "relation" attribute, the node relation set that allowed the matching between the subgraph and the PQG is stored...


```python
qs.relation
```




    [[{'alpha': True, 'fixed': True, 'label': 'a', 'tetha': {}, 'tetha_n': {}},
      (e4f6cb0:node {gender:"female",name:"l",type:"user"})],
     [{'alpha': True, 'fixed': False, 'label': 'b', 'tetha': {}, 'tetha_n': {}},
      (b5f4dc4:node {name:"h",type:"photo"})]]



Next, we evaluate automatically every defined PQG with every defined subgraph...


```python
Q = [q1,q2,q3,q4,q5,q6]
S = [s1,s2,s3]

l = []

for k1,s in enumerate(S):
    l.append([])
    for k2,q in enumerate(Q):
        l[k1].append(qs.query(q,s))
            
print tabulate(l)
```

    -  -  -  -  -  -
    0  0  1  1  0  0
    1  0  1  0  1  1
    1  0  1  1  0  1
    -  -  -  -  -  -

# Multi-Relational Decision Tree Learning

Now, we demonstrate the power of the **PQG-ID3** library. First, we build a model, notice that the target field should be present in every node in the training set...


```python
modelo = Id3(7474,"neo4j","pytpytpyt","gender") #id3(port,neo4j_username,neo4j_password,target_field)
```

Creating a starting PQG composed by one empty node (with id "0")...


```python
q = Pqg()
q.addNode("0",True,{},True)
```

Learning the decision tree from a training set of nodes (represented by their neo4j id)...


```python
tree = modelo.execute(q , [[1],[3],[4],[6],[8],[9],[11],[13]])
```

Then we can analyze the learned tree...


```python
tree.draw()
```


![png](https://s30.postimg.org/h2rxsfeyp/tree_social1.png)

As we can observe in the resulting decision tree, every inner node in the tree is associated with a PQG that every structure that reach this tree node should match.

Following there are some other decision trees obtained from different Neo4j datasets. A decision trees that classify between actors and movies in TMDb dataset (https://neo4j.com/developer/movie-database/):

![png](https://s24.postimg.org/8v27kvd5x/tree_cine1.png)

A decision trees that classify between different races in The Hobbit dataset (http://neo4j.com/graphgist/c43ade7d259a77fe49a8):

![png](https://s23.postimg.org/r9cq7wpkr/tree_hobbit1.png)
