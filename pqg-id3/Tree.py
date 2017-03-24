import networkx as nx
import matplotlib.pyplot as plt
import os
import shelve
import matplotlib
import math
import pydot
from Aux import *
from Conf import *
from StringIO import StringIO
import os, shutil

class Tree(object):
    def __init__(self):
        self.childs = []
        self.data = None
        self.id = None 
        self.t_set = None

    def createNX(self,G,nrows):
        G.add_node(str(self.id))
        ax=plt.subplot(nrows, 4,len(G.nodes()))
        ax.set_title("PQG "+str(self.idl))
        self.data.draw()
        for c in self.childs:
            G = c.createNX(G,nrows)
            G.add_edge(str(self.id),str(c.id),{"label":""})
        return G

    def createNX_leafs(self,G,nrows,cont):
        G.add_node(str(self.id))
        label = "NONE"
        if hasattr(self, 'idl'):
            if "(" in self.idl:
                label = self.idl[self.idl.find("(")+1:self.idl.find(")")]
            else:
                label = ""
        else:        
            label = ""
        if label != "NONE" and label != "":
            ax=plt.subplot(nrows, 4,cont.cont)
            cont.cont += 1
            ax.set_title(label)
            self.data.draw()
        for c in self.childs:
            G = c.createNX_leafs(G,nrows,cont)
            G.add_edge(str(self.id),str(c.id),{"label":""})
        return G


    def draw(self):
        plt.figure(figsize=(15, 30))
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

    def createNX_compact(self,G):
        pydot_graph = self.data.draw_compact()
        # render pydot by calling dot, no file saved to disk
        if hasattr(self, 'idl'):
            if "(" in self.idl:
                label = self.idl[self.idl.find("(")+1:self.idl.find(")")] if hasattr(self, 'idl') else ""
            else:
                label = ""
        else:        
            label = ""
        if label != "NONE":
            G.add_node(pydot.Node(str(self.id),image=pydot_graph,label=label,labelloc="t",height="3"))
            for c in self.childs:
                G,ltemp = c.createNX_compact(G)
                if ltemp != "NONE":
                    G.add_edge(pydot.Edge(str(self.id),str(c.id)))
        return G,label

    #draw_compact dibuja el arbol con los pqg denro de los nodos y elimina las hojas que no clasifican!
    def draw_compact(self):
        plt.figure(figsize=(60, 120))
        plt.clf()
        G,temp7 = self.createNX_compact(pydot.Dot(graph_type='digraph'))
        pydot_graph = G
        # render pydot by calling dot, no file saved to disk
        png_str = pydot_graph.create_png(prog='dot')
        # treat the dot output string as an image file
        sio = StringIO()
        sio.write(png_str)
        sio.seek(0)
        img = matplotlib.image.imread(sio)
        plt.axis('off')
        plt.imshow(img)
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def draw_leafs(self):
        plt.figure(figsize=(15, 30))
        plt.clf()
        cont = Cont()
        g=self.createNX_leafs(nx.DiGraph(),(self.num_pqgs()+5)/4,cont)

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

