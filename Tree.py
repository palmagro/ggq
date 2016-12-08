import networkx as nx
import os
class Tree(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.data = None
        self.t_set = None
    def str1(self, level=0):
        ret = "     "*level+str(self.data)+str(self.t_set)+"\n\n"
        if (self.left):
            ret += self.left.str1(level+1)
        if (self.right):
            ret += self.right.str1(level+1)
        return ret

    def str2(self, level, G,n):
        G.add_node(str(self.data)+str(self.t_set))
        G.add_node("l"+str(level))
        G.add_node("r"+str(level))
        G.add_edge(str(self.data)+str(self.t_set),"l"+str(level,G,"l"+str(level)))
        G.add_edge(str(self.data)+str(self.t_set),"r"+str(level,G,"r"+str(level)))
        G = self.left.str2(level+1,G,)
        ret = "     "*level+str(self.data)+str(self.t_set)+"\n\n"
        if (self.left):
            ret += self.left.str1(level+1)
        if (self.right):
            ret += self.right.str1(level+1)
        return ret

    def createNX(self,G):
        G.add_node(str(self.data)+str(self.t_set))
        if(self.left):
            G = self.left.createNX(G)
            G.add_edge(str(self.data)+str(self.t_set),str(self.left.data)+str(self.left.t_set))
        if(self.right):
            G = self.right.createNX(G)
            G.add_edge(str(self.data)+str(self.t_set),str(self.right.data)+str(self.right.t_set))
        return G
