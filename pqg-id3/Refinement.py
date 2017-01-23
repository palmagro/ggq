import uuid
import copy
import random
from Pqg import * 

class Refinement(object):
    def __init__(self,op,node,node_prop_link_type,value=None):
        self.op = op
        self.node = node
        self.type = node_prop_link_type
        if (value):
            self.value = value

    def refine(self,query):
        temp = str(len(query.nodes))
        query1 = Pqg()
        for n in query.nodes:
            query1.nodes.append(n)
        for l in query.links:
            query1.links.append(l)
        if self.op == "a":
            query1.addNode(temp ,True,{},False)
            query1.addLink(True,[self.node,temp],"-[:"+self.type+"]->",False)
            return query1
        if self.op == "b":
            query1.addNode(temp ,True,{},False)
            query1.addLink(True,[temp,self.node],"-[:"+self.type+"]->",False)
            return query1
        if self.op == "c":
            node = filter(lambda x: x["label"] == self.node,  query1.nodes)[0]
            print node
            print self.type
            node["tetha"][self.type] = self.value
            return query1
        if self.op == "ca":
            query1.addNode(temp ,False,{},False)
            query1.addLink(False,[self.node,temp],"-[:"+self.type+"]->",False)
            return query1
        if self.op == "cb":
            query1.addNode(temp ,False,{},False)
            query1.addLink(False,[temp,self.node],"-[:"+self.type+"]->",False)
            return query1
        if self.op == "cc":
            node = filter(lambda x: x["label"] == self.node,  query1.nodes)[0]
            node["tetha_n"][self.type] = self.value
            return query1

    def complement(self):
        if self.op == "a":
            return Refinement("ca",self.node,self.type)
        if self.op == "b":
            return Refinement("cb",self.node,self.type)
        if self.op == "c":
            print self.value
            return Refinement("cc",self.node,self.type,self.value)
