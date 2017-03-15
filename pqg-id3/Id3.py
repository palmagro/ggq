from py2neo import Graph
from Pqg import *
from Qsystem import *
from Tree import *
from Refinement import *
from scipy import stats
import collections
import os
import copy
import logging
from Aux import * 
from collections import Counter

class Id3:
    
    def __init__(self,port,user,password,target):
        self.graph = Graph("http://"+user+":"+password+"@localhost:"+str(port)+"/db/data/")
        self.qs = Qsystem(7474,"neo4j","123456789")
        self.refs = ["a","b","c","d"]
        self.target = target
        cypher = "MATCH (n)-[r]->(m) WITH type(r) as via RETURN distinct(via)"
        self.types = recordToList(self.graph.run(cypher),"via")
        cypher = "MATCH (n) RETURN keys(n)"
        temp = recordToList(self.graph.run(cypher),"keys(n)")
        self.n_props = []
        self.values = {}
        for t in temp:
            for i in t:
                if not i in self.values:
                    self.n_props.append(i)
                    self.values[i] = []
        for v in self.values:
            cypher = "MATCH (n) RETURN distinct(n."+v+")"
            self.values[v] = recordToList(self.graph.run(cypher),"(n."+v+")")[1:]
        self.cont = 0

    def execute_all_nodes(self,query, t_node,rec):
        print "comenzando ejecucion all"
        cypher = "MATCH (n:"+t_node+") RETURN id(n)"
        ids = recordToList(self.graph.run(cypher),"id(n)")
        temp = []
        for i in ids:
            temp.append([i])
        return self.execute(query,temp,rec)
    #EVALUAR SOLO LAS PROPIEDADES
    def execute(self,query, t_set,rec):
        print "comenzando ejecucion"
        self.cont += 1
        tree = Tree()
        tree.t_set = t_set
        tree.id = "n"+str(self.cont)
        tree.idl = "n"+str(self.cont)
        tree.data = Refinement("","","").clone_query(query)
        if self.stopCondition(t_set):
            tree.idl = "n"+str(self.cont)+"("+str(self.leaf(t_set))+")"
            tree.id = "n"+str(self.cont)
            return tree
        query.checkNodes()
        if not query.links:
            print "poraski"
        #vs = [x for x in query.nodes if x["fixed"] and x["alpha"]][0]
        #vns = [x for x in query.nodes if not x["fixed"] and ["alpa"]][0]
        #if not [e for e in query.links if e["gamma"][0] == vs["label"] and e["gamma"][1] == vns["label"]]:
            delta = Refinement("a",query.nodes[0],query.nodes[1])
        else:
#            if not [e for e in query.links if e["gamma"][0] == vns["label"] and e["gamma"][1] == vs["label"]]:
#                delta = Refinement("a",vns,vs)
#            else:
            delta = self.bestRefinement(query,t_set)

        print "todos"
        print t_set
        checks = []
        if rec > 0 and delta:
            tree.childs = []
            for idx,q in enumerate(delta.refine(query)):
                t_set_q = filter(lambda x: self.qs.query(q,x,[]), [x for x in t_set if x not in checks])
                checks += t_set_q
                print "hijo "+str(idx)
                print t_set_q
                tree.childs.append(self.execute(q,t_set_q,rec - 1))
        else:
            tree.idl = "n"+str(self.cont)+"("+str(self.leaf_aprox(t_set))+")"
            tree.target = str(self.leaf_aprox(t_set))
        return tree
        
    def stopCondition(self,t_set):
        l = self.getTargets(t_set)
        #print l
        return l[1:] == l[:-1]

    def leaf(self,t_set):
        ms = self.getTargets(t_set)
        if len(ms)>0:
            return ms[0]
        else:
            return "NONE"

    def leaf_aprox(self,t_set):
        ms = self.getTargets(t_set)
        if len(ms)>0:
            return str(max(set(ms), key=ms.count))+"("+str("%.2f" % (float(Counter(ms).most_common(1)[0][1])/len(ms)))+")"
        else:
            return "NONE"

    def bestRefinement(self,query,t_set): 
        ms = self.getTargets(t_set)
        counter=collections.Counter(ms)
        entropy = stats.entropy(counter.values())
        maxgain = -999999
        #CHECKING INFORMATION GAIN OF LTYPE REFINEMENT
        for op in self.refs:
            if op == "a" or op == "b":
                vals1 = [x for x in query.nodes if x["alpha"]]
                vals2 = vals1
            if op == "c":
                vals1 = [x for x in query.links if x["alpha"]]
                #types son los tipos de aristas
                vals2 = self.types
            if op == "d":
                vals1 = [x for x in query.nodes if x["alpha"] and all(query.getNode(i)["alpha"] for i in query.getInNeighs(x["label"])+query.getOutNeighs(x["label"]))]
                vals2 = []
                #n_props son las props de los nodos,
                for p in self.n_props:
                    if p != self.target:
                        #n_values(p) son los valores existentes de la propiedad p de los nodos,
                        for v in self.values[p]:
                            vals2.append(str(p)+":'"+str(v)+"'")
            for v1 in vals1:
                for v2 in vals2:
                        checks = []
                        delta = Refinement(op,v1,v2)
                        refs = delta.refine(query)
                        new_entropy = 0
                        for query_p in refs:
                            #print [x for x in t_set if x not in checks]
                            t_set_p = filter(lambda x: self.qs.query(query_p,x,[]), [x for x in t_set if x not in checks])
                            checks += t_set_p
                            #print checks
                            #print [x for x in t_set if x not in checks]
                            msp = self.getTargets(t_set_p)
                            freqp=collections.Counter(msp)  
                            new_entropy += (float(len(t_set_p))/len(t_set))*stats.entropy(freqp.values())
                        gain = entropy - new_entropy
                        #print "query: " + str(op)+ str(v1)+ str(v2)
                        #print entropy
                        #print new_entropy
                        #print gain
                        #gain = float(gain) / float(entropy)
                        #print gain
                        if gain > maxgain:
                            maxgain = gain
                            bestop = op
                            bestv1 = v1
                            bestv2 = v2
        print "best query: " + str(bestop)+ str(bestv1)+ str(bestv2)
        print "best ganancia: " + str(maxgain)
        if maxgain > 0:
            return Refinement(bestop,bestv1,bestv2)
        else:
            return False

    def getTargets(self,t_set):
        if len(t_set) == 0:
            return []
        cypher = "MATCH (n) where "
        for e in t_set:
            cypher += "id(n) = " + str(e[0]) + " or "
        cypher = cypher[:-3]
        cypher += " RETURN n."+self.target
        ms = self.graph.run(cypher)
        l = []
        for m in ms:
            l.append(m[0])
        return l


