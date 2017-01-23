import networkx as nx
import matplotlib.pyplot as plt
import os
class Tree(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.data = None
        self.id = None 
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
        G.add_node(str(self.id))
        #plt.suptitle(len(G.nodes()))
        plt.subplot(4, 4, len(G.nodes())+8, title="PQG "+str(self.id))
        self.data.draw()
        if(self.left):
            G = self.left.createNX(G)
            G.add_edge(str(self.id),str(self.left.id),{"label":"+"})
        if(self.right):
            G = self.right.createNX(G)
            G.add_edge(str(self.id),str(self.right.id),{"label":"-"})
        return G

    def draw(self):
        plt.clf()
        plt.subplot(4, 1, 1)
        g=self.createNX(nx.Graph())
        plt.subplot(2, 1, 1, title="Decission Tree")
        #print str(self.id)
        pos=self.hierarchy_pos(g,str(self.id))
        nx.draw(g,with_labels=True,pos=pos)
        edge_labels = {i[0:2]:'{}'.format(i[2]['label']) for i in g.edges(data=True)}
        nx.draw_networkx_edge_labels(g,pos,font_size=9,alpha=10,edge_labels=edge_labels) 
#        cont = 1
#        for n,p in pos.items():
#            plt.text(pos[n][0], pos[n][1], s, fontsize=12)

    def hierarchy_pos(self,G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5,pos = None, parent = None):
        if pos == None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        neighbors = sorted(G.neighbors(root))
        if parent != None:
            neighbors.remove(parent)
        if len(neighbors)!=0:
            dx = width/len(neighbors) 
            nextx = xcenter - width/2 - dx/2
            for neighbor in neighbors:
                nextx += dx
                pos = self.hierarchy_pos(G,neighbor, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                    parent = root)
        return pos

    def not_leafs(self,i):
        i+=1
        if(self.left):
            i1 += self.left.not_leafs(i)
        if(self.right):
            i2 += self.right.not_leafs(i)
        return max(i1,i2) 

