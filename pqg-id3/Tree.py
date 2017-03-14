import networkx as nx
import matplotlib.pyplot as plt
import os
import shelve
import matplotlib
import math
from StringIO import StringIO

class Tree(object):
    def __init__(self):
        self.childs = []
        self.data = None
        self.id = None 
        self.t_set = None

    def createNX(self,G,nrows):
        G.add_node(str(self.id))
        ax=plt.subplot(nrows, 4,len(G.nodes())+8)
        ax.set_title("PQG "+str(self.idl))
        self.data.draw()
        for c in self.childs:
            G = c.createNX(G,nrows)
            G.add_edge(str(self.id),str(c.id),{"label":""})
        return G

    def draw(self):
        plt.figure(figsize=(60, 120))
        plt.clf()
        g=self.createNX(nx.DiGraph(),(self.num_pqgs()+12)/4)

        plt.subplot((self.num_pqgs()+12)/8, 1, 1)
        pydot_graph = nx.drawing.nx_pydot.to_pydot(g)
        # render pydot by calling dot, no file saved to disk
        png_str = pydot_graph.create_png(prog='dot')
        # treat the dot output string as an image file
        sio = StringIO()
        sio.write(png_str)
        sio.seek(0)
        img = matplotlib.image.imread(sio)
        plt.axis('off')
        plt.imshow(img)
        #pos=self.hierarchy_pos(g,str(self.id))
        #nx.draw(g,with_labels=True,pos=pos,font_size=8)
        #edge_labels = {i[0:2]:'{}'.format(i[2]['label']) for i in g.edges(data=True)}
        #nx.draw_networkx_edge_labels(g,pos,font_size=9,alpha=10,edge_labels=edge_labels) 

    def hierarchy_pos(self,G, root, width=2., vert_gap = .2, vert_loc = 0, xcenter = 0.5,pos = None, parent = None):
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
        maxx = 0
        for c in self.childs:
            maxx = max(maxx,c.not_leafs(i))
        return maxx

    def save(self,name):
        database = shelve.open("trees.pqg")
        database[name] = self

    def load(self,name):
        database = shelve.open("trees.pqg")
        self.childs = database[name].childs
        self.data = database[name].data
        self.id = database[name].id
        self.idl = database[name].idl
        self.t_set = database[name].t_set

    def listar(self):
        database = shelve.open("trees.pqg")
        for d in database:
            print d

    def num_pqgs(self):
        num = 1
        for c in self.childs:
            num += c.num_pqgs()
        return num

