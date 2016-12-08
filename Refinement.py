import uuid
import copy
import random
from PropertyQueryGraph import *
class Refinement(object):
    def __init__(self,op,node,ltype):
        self.op = op
        self.node = node
        self.ltype = ltype

    def refine(self,query):
        #Cuidado que he tenido que cortar el uuuid a los 5 primeros chars porque no funcionaba y ahora no es unico!
        temp = str(len(query.nodes))#str(uuid.uuid4().hex)
        query1 = PropertyQueryGraph()
        for n in query.nodes:
            query1.nodes.append(n)
        for l in query.links:
            query1.links.append(l)
        if self.op == "a":
            query1.addNode(temp ,True,{},False)
            query1.addLink(True,[self.node,temp],"-[:"+self.ltype+"]->",False)
            return query1
        if self.op == "b":
            query1.addNode(temp ,True,{},False)
            query1.addLink(True,[temp,self.node],"-[:"+self.ltype+"]->",False)
            return query1
        if self.op == "c":
            query1.addNode(temp ,False,{},False)
            query1.addLink(False,[self.node,temp],"-[:"+self.ltype+"]->",False)
            return query1
        if self.op == "d":
            query1.addNode(temp ,False,{},False)
            query1.addLink(False,[temp,self.node],"-[:"+self.ltype+"]->",False)
            return query1

    def complement(self):
        if self.op == "a":
            return Refinement("c",self.node,self.ltype)
        if self.op == "b":
            return Refinement("d",self.node,self.ltype)
