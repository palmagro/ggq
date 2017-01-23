#AHORA MISMO EL PROBLEMA ED Q EL REF C NO ESTA MACHACANDO TB EL QUERY EN L RAMA POSITIVA!


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
        print "Creando nodo con query: " + str(query) + " y t_set: " + str(t_set)
        tree.id = "n"+str(self.cont)
        self.cont += 1
        if self.stopCondition(t_set):
            #os.write(1, "STOPCONDITION ALCANZADA")
            tree.data = query
            tree.id = "n"+str(self.cont)+"("+str(self.leaf(t_set))+")"
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
        tree.data = query
        return tree
        
    def stopCondition(self,t_set):
        l = self.getTargets(t_set)
        logging.warn("Lista de generos para verificar stopcondition:" + str(l))
        return l[1:] == l[:-1]

    def leaf(self,t_set):
        ms = self.getTargets(t_set)
        if len(ms)>0:
            return ms[0]
        else:
            return "NINGUNO"


    def bestRefinement(self,query,t_set): 
        ms = self.getTargets(t_set)
        counter=collections.Counter(ms)
        entropy = stats.entropy(counter.values())
        maxgain = -999999
        #CHECKING INFORMATION GAIN OF LTYPE REFINEMENT
        for op in self.refs:
            #os.write(1,str(len(query.nodes)))
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
                        #logging.warn("query_p (evaluando gain) " + str(query_p))                    
                        #logging.warn("Ejemplos a rama positiva (evaluando gain) " + str(t_set_p))
                        msp = self.getTargets(t_set_p)
                        freqp=collections.Counter(msp)
                        t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
                        #logging.warn("query_n (evaluando gain) " + str(query_n))                    
                        #logging.warn("Ejemplos a rama negativa (evaluando gain) " + str(t_set_n))
                        msn = self.getTargets(t_set_n)
                        freqn=collections.Counter(msn)
                        gain = entropy - (stats.entropy(freqp.values()) + stats.entropy(freqn.values()))
                        logging.warn(logging.warn("query: " + str(query_p)))
                        logging.warn("ganancia: " + str(gain))
                        if gain > maxgain:# and gain != 0: #HE PUESTO UNA TRAMPA EN LA GANANCIA DE INFORMACION VERIFICANDO QUE NO SEA IGUAL A 0, PORQUE LA ENTROPIA NO ESTA FUNCIONANDO BIEN
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
                            #logging.warn("query_p (evaluando gain) " + str(query_p))                    
                            #logging.warn("Ejemplos a rama positiva (evaluando gain) " + str(t_set_p))
                            msp = self.getTargets(t_set_p)
                            freqp=collections.Counter(msp)
                            t_set_n = filter(lambda x: self.qs.query(query_n,x), t_set)
                            #logging.warn("query_n (evaluando gain) " + str(query_n))                    
                            #logging.warn("Ejemplos a rama negativa (evaluando gain) " + str(t_set_n))
                            msn = self.getTargets(t_set_n)
                            freqn=collections.Counter(msn)
                            gain = entropy - (stats.entropy(freqp.values()) + stats.entropy(freqn.values()))
                            logging.warn(logging.warn("query: " + str(query_p)))
                            logging.warn("ganancia: " + str(gain))
                            if gain > maxgain:# and gain != 0: #HE PUESTO UNA TRAMPA EN LA GANANCIA DE INFORMACION VERIFICANDO QUE NO SEA IGUAL A 0, PORQUE LA ENTROPIA NO ESTA FUNCIONANDO BIEN
                                maxgain = gain
                                bestop = op
                                bestn = n["label"]
                                bestt = t
        print "MEJOR REFINAMIENTO"
        print bestop
        print bestn
        print bestt
        print "maxima ganancia"
        print maxgain
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
        #print ms
#        if l[0][0]:
#            for id,m in enumerate(l):
#                l[id] = m[0]
        #print "LOS TARGETS"
        #print l        
        return l
