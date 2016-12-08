from py2neo import Graph
from PropertyQueryGraph import *
from QuerySystem import *
from Tree import *
from Refinement import *
from scipy import stats
import collections
import os
import copy
from aux import * 
class id3:
    
    def __init__(self,target,refs):
        self.graph = Graph("http://neo4j:pytpytpyt@localhost:7474/db/data/")
        self.qs = QuerySystem(7474,"neo4j","123456789")
        self.refs = refs
        self.target = target
        cypher = "MATCH (n)-[r]->(m) WITH type(r) as via RETURN   distinct(via)"
        self.types = recordToList(self.graph.run(cypher),"via")

    def execute(self,query, t_set):
        tree = Tree()
        tree.t_set = t_set
        os.write(1,"Creando nodo con query: " + str(query) + " y t_set: " + str(t_set))
        if self.stopCondition(t_set):
            #os.write(1, "STOPCONDITION ALCANZADA")
            tree.data = self.leaf(t_set)
            return tree
        #os.write(1, "OBTENIENDO MEJOR REF")
        delta = self.bestRefinement(query,t_set)
        c_delta = delta.complement()
        #os.write(1, "REFINANDO")
        query_p = delta.refine(query)
        query_n = c_delta.refine(query)
        #os.write(1, "FILTRANDO")
        t_set_p = filter(lambda x: self.qs.query(query_p,x), t_set)
        t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
        os.write(1,"Ejemplos a rama positiva" + str(t_set_p))
        os.write(1,"Ejemplos a rama negativa" + str(t_set_n))
        tree_p = self.execute(query_p,t_set_p)
        os.write(1,str(tree_p.data))
        tree_n = self.execute(query_n,t_set_n)
        tree.right = tree_n
        tree.left = tree_p
        tree.data = query_p
        return tree
        
    def stopCondition(self,t_set):
        ms = self.getTargets(t_set)
        l = []
        for m in ms:
            logging.debug(m["n.gender"])
            l.append(m["n.gender"])
        logging.warn("Lista de generos para verificar stopcondition:" + str(l))
        return l[1:] == l[:-1]

    def leaf(self,t_set):
        ms = self.getTargets(t_set)
        for m in ms:
            return m["n.gender"]


    def bestRefinement(self,query,t_set):
        ms = self.getTargets(t_set)
        counter=collections.Counter(ms)
        entropy = stats.entropy(counter.values())
        maxgain = -0.1
        #os.write(1,str(len(self.refs)))
        for op in self.refs:
            #os.write(1,str(len(query.nodes)))
            for t in self.types:
                for n in query.nodes:
                    #os.write(1, op)
                    r = Refinement(op,n["label"],t)
                    query_p = r.refine(query)
                    c_r = r.complement()
                    query_n = c_r.refine(query)
                    t_set_p = filter(lambda x: self.qs.query(query_p,x), t_set)
                    logging.warn("query_p (evaluando gain) " + str(query_p))                    
                    logging.warn("Ejemplos a rama positiva (evaluando gain) " + str(t_set_p))
                    msp = self.getTargets(t_set_p)
                    freqp=collections.Counter(msp)
                    t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
                    logging.warn("query_n (evaluando gain) " + str(query_n))                    
                    logging.warn("Ejemplos a rama negativa (evaluando gain) " + str(t_set_n))
                    msn = self.getTargets(t_set_n)
                    freqn=collections.Counter(msn)
                    gain = entropy - (stats.entropy(freqp.values()) + stats.entropy(freqn.values()))
                    logging.warn("query: " + str(query_p))
                    logging.warn("ganancia: " + str(gain))
                    if gain > maxgain:
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
        return self.graph.run(cypher)
