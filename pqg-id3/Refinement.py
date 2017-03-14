import uuid
import copy
import random
import itertools
from Pqg import * 

class Refinement(object):
    #val1: Node1 en operador anadir arista, arista en anadir prop a arista, Node en anadir prop a Node.
    #val2: Node2 en operador anadir arista, prop en anadir prop a arista, prop en anadir prop a Node
    def __init__(self,op,val1,val2):
        self.op = op
        self.val1 = val1
        self.val2 = val2

    def refine(self,query):
        refs = []
        #ANADIR ARISTA POSITIVA ENTRE NodeS +
        if self.op == "a":
            #si es un lazo:
            if self.val1["label"] == self.val2["label"]:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(self.val1["label"]),True)
                q1.addLink(True,[n1["label"],n1["label"]],"",False)
                q1.deleteNode(self.val1["label"])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(self.val1["label"]),True)
                n2 = q2.cloneNode(q2.getNode(self.val2["label"]),False)
                q2.addLink(True,[n2["label"],n2["label"]],"",False)
                q2.deleteNode(self.val1["label"])
                refs.append(q2)
            #si no lo es:
            else:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(self.val1["label"]),True)
                n2 = q1.cloneNode(q1.getNode(self.val2["label"]),True)
                q1.addLink(True,[n1["label"],n2["label"]],"",False)
                q1.deleteNode(self.val1["label"])
                q1.deleteNode(self.val2["label"])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(self.val1["label"]),True)
                n2 = q2.cloneNode(q2.getNode(self.val2["label"]),False)
                q2.addLink(True,[n1["label"],n2["label"]],"",False)
                q2.deleteNode(self.val1["label"])
                refs.append(q2)

                q3 = self.clone_query(query)
                n1 = q3.cloneNode(q3.getNode(self.val1["label"]),False)
                n2 = q3.cloneNode(q3.getNode(self.val2["label"]),True)
                q3.addLink(True,[n1["label"],n2["label"]],"",False)
                q3.deleteNode(self.val2["label"])
                refs.append(q3)

                q4 = self.clone_query(query)
                n1 = q4.cloneNode(q4.getNode(self.val1["label"]),False)
                n2 = q4.cloneNode(q4.getNode(self.val2["label"]),False)
                q4.addLink(True,[n1["label"],n2["label"]],"",False)
                refs.append(q4)

            return refs

        #ANADIR ARISTA NEGATIVA ENTRE NodeS +
        if self.op == "b":
            #si es un lazo:
            if self.val1["label"] == self.val2["label"]:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(self.val1["label"]),True)
                q1.addLink(False,[n1["label"],n1["label"]],"",False)
                q1.deleteNode(self.val1["label"])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(self.val1["label"]),True)
                n2 = q2.cloneNode(q2.getNode(self.val2["label"]),False)
                q2.addLink(False,[n2["label"],n2["label"]],"",False)
                q2.deleteNode(self.val1["label"])
                refs.append(q2)
            #si no lo es:
            else:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(self.val1["label"]),True)
                n2 = q1.cloneNode(q1.getNode(self.val2["label"]),True)
                q1.addLink(False,[n1["label"],n2["label"]],"",False)
                q1.deleteNode(self.val1["label"])
                q1.deleteNode(self.val2["label"])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(self.val1["label"]),True)
                n2 = q2.cloneNode(q2.getNode(self.val2["label"]),False)
                q2.addLink(False,[n1["label"],n2["label"]],"",False)
                q2.deleteNode(self.val1["label"])
                refs.append(q2)

                q3 = self.clone_query(query)
                n1 = q3.cloneNode(q3.getNode(self.val1["label"]),False)
                n2 = q3.cloneNode(q3.getNode(self.val2["label"]),True)
                q3.addLink(False,[n1["label"],n2["label"]],"",False)
                q3.deleteNode(self.val2["label"])
                refs.append(q3)

                q4 = self.clone_query(query)
                n1 = q4.cloneNode(q4.getNode(self.val1["label"]),False)
                n2 = q4.cloneNode(q4.getNode(self.val2["label"]),False)
                q4.addLink(False,[n1["label"],n2["label"]],"",False)
                refs.append(q4)

            return refs

        #ANADIR PRED A ARISTA +
        if self.op == "c":
            e = self.val1
            #si es un lazo:
            if e["gamma"][0] == e["gamma"][1]:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(e["gamma"][0]),True)
                e1 = q1.getLink(True,[n1["label"],n1["label"]],e["tetha"],e["fixed"])    
                q1.addPredE(e1,self.val2)
                q1.deleteNode(e["gamma"][0])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(e["gamma"][0]),True)
                n2 = q2.cloneNode(q2.getNode(e["gamma"][0]),False)
                e2 = q2.getLink(True,[n2["label"],n2["label"]],e["tetha"],e["fixed"])    
                q2.addPredE(e2,self.val2)
                q2.deleteNode(e["gamma"][0])
                refs.append(q2)
            #si no lo es:
            else:
                q1 = self.clone_query(query)
                n1 = q1.cloneNode(q1.getNode(e["gamma"][0]),True)
                n2 = q1.cloneNode(q1.getNode(e["gamma"][1]),True)
                e1 = q1.getLink(True,[n1["label"],n2["label"]],e["tetha"],e["fixed"])    
                q1.addPredE(e1,self.val2)
                q1.deleteNode(e["gamma"][0])
                q1.deleteNode(e["gamma"][1])
                refs.append(q1)

                q2 = self.clone_query(query)
                n1 = q2.cloneNode(q2.getNode(e["gamma"][0]),True)
                n2 = q2.cloneNode(q2.getNode(e["gamma"][1]),False)
                e2 = q2.getLink(True,[n1["label"],n2["label"]],e["tetha"],e["fixed"])    
                q2.addPredE(e2,self.val2)
                q2.deleteNode(e["gamma"][0])
                refs.append(q2)
                
                q3 = self.clone_query(query)
                n1 = q3.cloneNode(q3.getNode(e["gamma"][0]),False)
                n2 = q3.cloneNode(q3.getNode(e["gamma"][1]),True)
                e3 = q3.getLink(True,[n1["label"],n2["label"]],e["tetha"],e["fixed"])    
                q3.addPredE(e3,self.val2)
                q3.deleteNode(e["gamma"][1])
                refs.append(q3)

                q4 = self.clone_query(query)
                n1 = q4.cloneNode(q4.getNode(e["gamma"][0]),False)
                n2 = q4.cloneNode(q4.getNode(e["gamma"][1]),False)
                e4 = q4.getLink(True,[n1["label"],n2["label"]],e["tetha"],e["fixed"])    
                q4.addPredE(e4,self.val2)
                refs.append(q4)
            return refs

        #ANADIR PRED A Node +
        if self.op == "d":
            alphas = []
            n_neigh = len(query.getInNeighs(self.val1["label"]))+len(query.getOutNeighs(self.val1["label"]))
            #print n_neigh
            #print query.links
            for j in itertools.product((True,False), repeat=n_neigh+1) :
                alphas.append(j)
            #print alphas
            for a in alphas:
                #print "ref"
                qn = self.clone_query(query)
                #print qn
                n1 = qn.cloneNodeNeighbors(self.val1,a)
                qn.addPredN(n1,self.val2)
                refs.append(qn)
                #print qn
            return refs

    def clone_query(self,query):
        query1 = Pqg()
        for n in query.nodes:
            query1.nodes.append(n.copy())
        for l in query.links:
            query1.addLink(l["alpha"],[l["gamma"][0],l["gamma"][1]],l["tetha"],l["fixed"])
        return query1
