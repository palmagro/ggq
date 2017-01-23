import networkx as nx
import matplotlib.pyplot as plt

class PropertyQueryGraph:
    nodes = []
    links = [] 

    def __init__(self):
        self.nodes = []
        self.links = []

    def addNode(self,label,alpha,tetha,fixed):
        self.nodes.append({"label":label,"alpha":alpha,"tetha":tetha,"tetha_n":{},"fixed":fixed})

    def addLink(self,alpha,gamma,tetha,fixed):
        self.links.append({"alpha":alpha,"gamma":gamma,"tetha":tetha,"fixed":fixed})

    def getPresentLinks(self,name):
        outlinks = [x for x in self.links if x["alpha"] and name in x["gamma"][0]]
        inlinks = [x for x in self.links if x["alpha"] and name in x["gamma"][1]]
        for o in outlinks:
            o["inverse"] = False
        for i in inlinks:
            i["inverse"] = True
        return outlinks+inlinks

    def getAbsentLinks(self,name):
        outlinks = [x for x in self.links if not x["alpha"] and name in x["gamma"][0]]
        inlinks = [x for x in self.links if not x["alpha"] and name in x["gamma"][1]]
        for o in outlinks:
            o["inverse"] = False
            o["other_node"] = o["gamma"][1]
        for i in inlinks:
            i["inverse"] = True
            i["other_node"] = i["gamma"][0]
        return outlinks+inlinks

    def createNX(self,G):
        for n in self.nodes:
            G.add_node(n["label"],{"label":n["label"],"color":int(n["alpha"])})
        for e in self.links:
            G.add_edge(e["gamma"][0],e["gamma"][1],{"tetha":e["tetha"],"color":(int(e["alpha"]))})
        return G

    def draw(self):
        g=self.createNX(nx.DiGraph())
        pos=nx.spring_layout(g) 
        nx.draw(g,pos, with_labels=True)
        node_colors = [i[1]['color'] for i in g.nodes(data=True)]
        nx.draw_networkx_nodes(g,pos=pos,node_color=node_colors,vmin=0,vmax=1,cmap=plt.cm.autumn)
        edge_labels = {i[0:2]:'{}'.format(i[2]['tetha']) for i in g.edges(data=True)}
        edge_colors = [i[2]['color'] for i in g.edges(data=True)]
        nx.draw_networkx_edges(g,pos,label="tetha",font_size=9,edge_color= edge_colors,edge_vmin=0,edge_vmax=1,edge_cmap=plt.cm.autumn,width=4)
        for n,p in pos.items():
            pos[n][1] +=0.1;
        nx.draw_networkx_edge_labels(g,pos,font_size=9,edge_labels=edge_labels)

    def __str__(self):
        return str(self.nodes) + str(self.links)
