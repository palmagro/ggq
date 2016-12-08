from py2neo import Graph
import itertools
from random import shuffle
import logging

class QuerySystem:

    def __init__(self,port,user,pss):
        self.port = port
        self.user = user
        self.pss = pss
        self.pairs = []
        self.subgraph_nodes = []
        self.q = {}
        self.relation = []
        self.ignorables = ["name","fixed","alpha","tetha","inverse","other_node","label"]
        self.graph = Graph("http://"+self.user+":"+self.pss+"@localhost:"+str(self.port)+"/db/data/")

    def query(self,query,subgraph_nodes):
        self.subgraph_nodes = subgraph_nodes
        self.q = query
        #In self.V we will save all pairs (set of pairs of query_node-subgraph_node)
        self.pairs = []
        #Store query nodes fixed and open
        fixed = [x for x in query.nodes if x["fixed"] and x["alpha"]]
        #Store subgraph nodes
        self.subgraph_nodes = map(lambda x: self.graph.node(x),subgraph_nodes)
        #Iterating over all possible pairs
        for s in self.subgraph_nodes:
            for f in fixed:
                self.pairs.append([s,f])                
        #If there is not 1 pair at least, return False!
        if len(self.pairs) == 0:
            return False
        #We will verify if any of the pairs can construct a complete isomorphism!
        for p in self.pairs:
            self.relation = []
            if self.check_nodes(p[0],p[1],[]):
                return True
        return False

    def isomorph(self,ns,nq):
        #Avoiding py2neo "capsule"
        if ns["m"]:
            ns = ns["m"]    
        if nq["fixed"] and ns not in self.subgraph_nodes:
            return False
        for key in nq["tetha"]:
            if key != "name" and key != "fixed" and key != "alpha" and key != "tetha":
                logging.debug("Verificando si la clave "+key+" existe en el nodo ")
                logging.debug(ns["name"])
                if not key in ns:
                    return False
                logging.debug("Verificando si el valor de la clave "+key+" es la correcta en el nodo "+ns["name"])
                if ns[key] != nq["tetha"][key]:
                    return False            
        return True

    def check_nodes(self,ns,nq,checks):
        #Avoiding py2neo "capsule"
        if ns["m"]:
            ns = ns["m"]   
        logging.debug("Verifying isomorphism between..")
        logging.debug(ns)
        logging.debug(nq)
        if not self.isomorph(ns,nq):
            return False
        logging.debug("Verifying absent edge restrictions..")
        ablinks = self.q.getAbsentLinks(nq["label"])
        logging.debug(ablinks)
        for a in ablinks:
            if a["inverse"]:
                cypher = "MATCH (m)"+a["tetha"]+"(n) where n.name = '"+str(ns["name"])+"'" 
                other_node = [x for x in self.q.nodes if x["label"] == a["other_node"]][0]
                for key in other_node:
                    if key not in self.ignorables:
                        cypher+="and m."+key+"='"+other_node[key]+"' "
                cypher += "RETURN m"
                ms = self.graph.run(cypher)
            else:
                cypher = "MATCH (n)"+a["tetha"]+"(m) where n.name = '"+str(ns["name"])+"'" 
                other_node = [x for x in self.q.nodes if x["label"] == a["other_node"]][0]
                logging.debug(other_node)
                for key in other_node:
                    if key not in self.ignorables:
                        cypher+="and m."+key+"='"+other_node[key]+"' "
                cypher += "RETURN m"
                logging.debug(cypher)
                ms = self.graph.run(cypher)
            if len(ms.data())>0:
                return False
        checks.append(nq)
        self.relation.append([nq,ns])
        logging.debug("nodes without check!")
        logging.debug([x for x in self.q.nodes if x["alpha"] and x not in checks])
        if len([x for x in self.q.nodes if x["alpha"] and x not in checks]) == 0:
            return True
        logging.debug("Present links..."        )
        links = self.q.getPresentLinks(nq["label"])
        shuffle(links)
        for l in links:
            logging.debug(l)
            if l["inverse"]:
                mss = self.graph.run("MATCH (m)"+l["tetha"]+"(n) where n.name = '"+str(ns["name"])+"' RETURN m")
            else:
                mss = self.graph.run("MATCH (n)"+l["tetha"]+"(m) where n.name = '"+str(ns["name"])+"' RETURN m")
            mss = mss.data()
            logging.debug("nodos al otro lado en el subgrafo")
            logging.debug(mss)
            if l["inverse"]:
                nqs = [x for x in self.q.nodes if x["alpha"] and x["label"] == l["gamma"][0]]
            else:
                nqs = [x for x in self.q.nodes if x["alpha"] and x["label"] == l["gamma"][1]]                
            logging.debug("nodos al otro lado en el query")
            logging.debug(nqs)
            result = False
            for m in mss:
                for n in nqs:
                    result = result or self.check_nodes(m,n,checks)            
            return result
