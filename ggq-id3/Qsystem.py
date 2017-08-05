from py2neo import Graph
import itertools
from random import shuffle
import logging

class Qsystem:

    def __init__(self,port,user,pss): 
        self.port = port
        self.user = user
        self.pss = pss
        self.pairs = []
        self.subgraph_nodes = []
        self.q = {}
        self.relation = []
        self.ignorables = ["name","fixed","alpha","tetha","tetha_n","inverse","other_node","label"]
        self.graph = Graph("http://"+self.user+":"+self.pss+"@localhost:"+str(self.port)+"/db/data/")
        logging.basicConfig(filename='example.log',level=logging.ERROR)

    def query(self,query,subgraph_nodes,subgraph_edges):
        result = True
        self.set_fixed(subgraph_nodes)
        for n in query.nodes:
            fixed_n = []
            consulta = "MATCH (a{"+self.enumerate_dict(n["tetha"])+(self.comasinovacio(self.enumerate_dict(n["tetha"]))+"inS:true" if n["fixed"] else "")+"}) "
            consulta += "WHERE "
#            if n["fixed"]:
#                consulta += "("
###                for sn in subgraph_nodes:
#                    consulta +="id(a) = "+str(sn)+" OR "
#                consulta += "False) AND "
            for idx,e in enumerate(query.getInLinks(n["label"])):
                if not e["alpha"]:
                    consulta += "NOT "
                consulta += "(a)<-["+e["tetha"]+"]-("
                consulta += "{"+self.enumerate_dict(query.getNode(e["gamma"][0])["tetha"])+self.comasinovacio(self.enumerate_dict(query.getNode(e["gamma"][0])["tetha"]))+("inS:true" if query.getNode(e["gamma"][0])["fixed"] else "inS:false")+"}"
                consulta += ") AND "
            for idx,e in enumerate(query.getOutLinks(n["label"])):
                if not e["alpha"]:
                    consulta += "NOT "
                consulta += "(a)-["+e["tetha"]+"]->("
                consulta += "{"+self.enumerate_dict(query.getNode(e["gamma"][1])["tetha"])+self.comasinovacio(self.enumerate_dict(query.getNode(e["gamma"][1])["tetha"]))+("inS:true" if query.getNode(e["gamma"][1])["fixed"] else "inS:false")+"}"
                consulta += ") AND "
            consulta += "True RETURN a LIMIT 1"
            #print consulta
            if n["alpha"]:
                result = result and (self.graph.run(consulta).forward() != 0)
                
            else:
                result = result and (self.graph.run(consulta).forward() == 0)  
                #print consulta   
                #print "valor fordward"
                #print self.graph.run(consulta).forward()
                #print "valor alpha"
                #print n["alpha"]
                #print "valor result"
                #print result           
        self.undo_fixed(subgraph_nodes)
        return result

    def enumerate_dict(self,tetha):
        if tetha == {}:
            for k in tetha:
                if k == "label":
                    return ":"+tetha[k]
                else:
                    string = "{"+tetha[0]
                    for k,v in enumerate(tetha[1:]):
                        string += ","+unicode(k)+":"+v

                    return string
        else:
            return tetha

    def set_fixed(self,nodes):
        consulta = "MATCH (n) WHERE id(n)="+unicode(nodes[0])+" SET n.inS = true"
        self.graph.run(consulta)
    def undo_fixed(self,nodes):
        consulta = "MATCH (n) WHERE id(n)="+unicode(nodes[0])+" SET n.inS = false"
        self.graph.run(consulta)
    def comasinovacio(self,s):
        if s == "":
            return ""
        else:
            return ","
