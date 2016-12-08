import uuid
import copy
from PropertyQueryGraph import *
class Refinement(object):
    def __init__(self,op,node):
        self.op = op
        self.node = node

    def refine(self,query):
        temp = "b"#uuid.uuid4().hex
        query1 = PropertyQueryGraph()
        for n in query.nodes:
            query1.nodes.append(n)
        for l in query.links:
            query1.links.append(l)
        if self.op == "a":
            query1.addNode(temp ,True,{},False)
            query1.addLink(True,[self.node,temp],"-[]->",False)
            return query1
        
        if self.op == "c":
            query1.addNode(temp ,False,{},False)
            query1.addLink(False,[self.node,temp],"-[]->",False)
            return query1

    def complement(self):
        if self.op == "a":
            return Refinement("c",self.node)
