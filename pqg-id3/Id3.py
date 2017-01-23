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
class Id3:
    
    def __init__(self,port,user,password,target):
        self.graph = Graph("http://"+user+":"+password+"@localhost:"+str(port)+"/db/data/")
        self.qs = Qsystem(7474,"neo4j","123456789")
        self.refs = ["a","b"]
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
        self.cont = 1

    def execute_all_nodes(self,query, t_node):
        cypher = "MATCH (n:"+t_node+") RETURN id(n)"
        ids = recordToList(self.graph.run(cypher),"id(n)")
        temp = []
        for i in ids:
            temp.append([i])
        return self.execute(query,temp)

    def execute(self,query, t_set):
        tree = Tree()
        tree.t_set = t_set
        tree.id = "n"+str(self.cont)
        self.cont += 1
        if self.stopCondition(t_set):
            tree.data = query
            tree.id = "n"+str(self.cont)+"("+str(self.leaf(t_set))+")"
            return tree
        delta = self.bestRefinement(query,t_set)
        c_delta = delta.complement()
        query_p = delta.refine(query)
        query_n = c_delta.refine(query)
        t_set_p = filter(lambda x: self.qs.query(query_p,x), t_set)
        t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
        tree_p = self.execute(query_p,t_set_p)
        tree_n = self.execute(query_n,t_set_n)
        tree.right = tree_n
        tree.left = tree_p
        tree.data = query
        return tree
        
    def stopCondition(self,t_set):
        l = self.getTargets(t_set)
        return l[1:] == l[:-1]

    def leaf(self,t_set):
        ms = self.getTargets(t_set)
        if len(ms)>0:
            return ms[0]
        else:
            return "NONE"


    def bestRefinement(self,query,t_set): 
        ms = self.getTargets(t_set)
        counter=collections.Counter(ms)
        entropy = stats.entropy(counter.values())
        maxgain = -999999
        #CHECKING INFORMATION GAIN OF LTYPE REFINEMENT
        for op in self.refs:
            prop_ref = not(op == "a" or op == "b")
            if prop_ref:
                tipos = self.n_props
            else:
                tipos = self.types
            for t in tipos:
                for n in query.nodes:
                    if not prop_ref:
                        r = Refinement(op,n["label"],t)
                        query_p = r.refine(query)
                        c_r = r.complement()
                        query_n = c_r.refine(query)
                        t_set_p = filter(lambda x: self.qs.query(query_p,x), t_set)
                        msp = self.getTargets(t_set_p)
                        freqp=collections.Counter(msp)
                        t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
                        msn = self.getTargets(t_set_n)
                        freqn=collections.Counter(msn)
                        gain = entropy - (stats.entropy(freqp.values()) + stats.entropy(freqn.values()))
                        logging.warn(logging.warn("query: " + str(query_p)))
                        logging.warn("ganancia: " + str(gain))
                        if gain > maxgain:# and gain != 0: 
                            maxgain = gain
                            bestop = op
                            bestn = n["label"]
                            bestt = t
                    #CHECKING INFORMATION GAIN OF ADDED PROPERTIES TO NODES REFINEMENT
                    else:
                        for v in self.values[t]:
                            print v
                            r = Refinement(op,n["label"],t,v)
                            query_p = r.refine(query)
                            c_r = r.complement()
                            query_n = c_r.refine(query)
                            t_set_p = filter(lambda x: self.qs.query(query_p,x), t_set)
                            msp = self.getTargets(t_set_p)
                            freqp=collections.Counter(msp)
                            t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
                            msn = self.getTargets(t_set_n)
                            freqn=collections.Counter(msn)
                            gain = entropy - (stats.entropy(freqp.values()) + stats.entropy(freqn.values()))
                            logging.warn(logging.warn("query: " + str(query_p)))
                            logging.warn("ganancia: " + str(gain))
                            if gain > maxgain:# and gain != 0: 
                                maxgain = gain
                                bestop = op
                                bestn = n["label"]
                                bestt = t
        return Refinement(bestop,bestn,bestt)

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
