import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import uuid
from StringIO import StringIO
from Conf import *
class Ggq:
    nodes = []
    links = [] 

    def __init__(self):
        self.nodes = []
        self.links = []

    def addNode(self,label,alpha,tetha,fixed):
        self.nodes.append({"label":label,"alpha":alpha,"tetha":tetha,"fixed":fixed})

    def addLink(self,alpha,gamma,tetha,fixed):
        e = {"alpha":alpha,"gamma":gamma,"tetha":tetha,"fixed":fixed}
        self.links.append(e)
        return e

    def addPredN(self,node,pred):
        if node["tetha"] == "":
            node["tetha"] += pred
        else:
            node["tetha"] += ","+pred
    def addPredE(self,edge,pred):
        if edge["tetha"] == "":
            edge["tetha"] += ":"+pred
        else:
            edge["tetha"] += "|"+pred


    def getNode(self,name):
        return filter(lambda obj: obj["label"] == str(name), self.nodes)[0]

    def getLink(self,alpha,gamma,tetha,fixed):
        return filter(lambda obj: obj["alpha"] == alpha and obj["gamma"] == gamma and obj["tetha"] == tetha and obj["fixed"] == fixed, self.links)[0]


    def deleteNode(self,label):
        self.nodes =  filter(lambda x : x["label"] != label, self.nodes) 
        temp = filter(lambda x : x["gamma"][0] != label, self.links)
        temp = filter(lambda x : x["gamma"][1] != label, temp)
        self.links = temp

    def getInLinks(self,name):
        return [x for x in self.links if name == x["gamma"][1] and name != x["gamma"][0]]

    def getOutLinks(self,name):
        return [x for x in self.links if name ==  x["gamma"][0] and name != x["gamma"][1]]

    def getInNeighs(self,name):
        return list(set([x["gamma"][0] for x in self.getInLinks(name)]))

    def getOutNeighs(self,name):
        return list(set([x["gamma"][1] for x in self.getOutLinks(name)]))

    def getLazos(self,name):
        return [x for x in self.links if name in x["gamma"][0] and name in x["gamma"][1]]

    def getPresentLinks(self,name):
        outlinks = [x for x in self.links if x["alpha"] and name in x["gamma"][0]]
        inlinks = [x for x in self.links if x["alpha"] and name in x["gamma"][1]]
        for o in outlinks:
            o["inverse"] = False
            o["other_node"] = o["gamma"][1]
        for i in inlinks:
            i["inverse"] = True
            i["other_node"] = i["gamma"][0]
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

    def cloneNode(self,n,alpha,node_ex=""):
        #excluimos las aristas que nos conectan con el nodo nex para permitir que el clonenodeneigh se efectue correctamente
        nex = node_ex
        temp = str(uuid.uuid4())
        self.addNode(temp,alpha,n["tetha"],n["fixed"])
        for l in self.getInLinks(n["label"]):
            if l["gamma"][0] != nex:
                self.addLink(l["alpha"],[l["gamma"][0],temp],l["tetha"],l["fixed"])
                #print [l["gamma"][0],temp]
        #print self.getOutLinks(n["label"])
        for l in self.getOutLinks(n["label"]):
            if l["gamma"][1] != nex:
                self.addLink(l["alpha"],[temp,l["gamma"][1]],l["tetha"],l["fixed"])
                #print [temp,l["gamma"][1]]
        #tratamos los lazos por separado
        for l in self.getLazos(n["label"]):        
            self.addLink(l["alpha"],[temp,temp],l["tetha"],l["fixed"])
        return self.getNode(temp)

    def cloneNodeNeighbors(self,n,alphas):
        temp = str(uuid.uuid4())
        cont = 0
        clones = {}
        self.addNode(temp,alphas[cont],n["tetha"],n["fixed"])
        #primero clonamos los lazos
        for l in self.getLazos(n["label"]):        
            self.addLink(l["alpha"],[temp,temp],l["tetha"],l["fixed"])
        cont += 1
        #print cont
        #print self.getInLinks(n["label"])
        for l in self.getInLinks(n["label"]):
            if l["gamma"][0] not in clones:
                #print "clonando"+l["gamma"][0]
                clones[l["gamma"][0]] = self.cloneNode(self.getNode(l["gamma"][0]),alphas[cont],node_ex=n["label"])
                if alphas[cont]:
                    self.deleteNode(l["gamma"][0])
                cont += 1
                #print cont
            m = clones[l["gamma"][0]]
            self.addLink(l["alpha"],[m["label"] if l["gamma"][0] != l["gamma"][1] else temp,temp],l["tetha"],l["fixed"])
            #print [temp,m["label"] if l["gamma"][0] != l["gamma"][1] else temp]
        #print self.getInLinks(n["label"])
        #print self.getOutLinks(n["label"])
        for l in self.getOutLinks(n["label"]):
            if l["gamma"][1] not in clones:
                #print "clonando"+l["gamma"][1]
                clones[l["gamma"][1]] = self.cloneNode(self.getNode(l["gamma"][1]),alphas[cont],node_ex=n["label"])
                if alphas[cont]:
                    self.deleteNode(l["gamma"][1])
                cont += 1
                #print cont
            m = clones[l["gamma"][1]]
            #print [temp,m["label"] if l["gamma"][0] != l["gamma"][1] else temp]
            self.addLink(l["alpha"],[temp,m["label"] if l["gamma"][0] != l["gamma"][1] else temp],l["tetha"],l["fixed"])
        #print self.getOutLinks(n["label"])
        if (alphas[0] and len(self.getInNeighs(n["label"]))+len(self.getOutNeighs(n["label"])) == 0) or all(item for item in alphas):
            self.deleteNode(n["label"])
        return self.getNode(temp)

    def checkNodes(self):
        resultG = False
        resultS = False
        for n in self.nodes:
            resultS = resultS or (n["fixed"] and self.getPresentLinks(n["label"])+self.getAbsentLinks(n["label"]) == [])
            resultG = resultG or (not n["fixed"] and self.getPresentLinks(n["label"])+self.getAbsentLinks(n["label"]) == [])
        if not resultS and len([x for x in self.nodes if x["fixed"]]) == 0:
            print len([x for x in self.nodes if x["fixed"]])
            temp = str(uuid.uuid4())
            self.addNode(temp,True,"",True)
        if not resultG:
            temp = str(uuid.uuid4())
            self.addNode(temp,True,"",False)

    def createNX(self,G):
        for n in self.nodes:
            #print n["tetha"]
            G.add_node(n["label"],{"label":n["tetha"]+("(v in S)" if n["fixed"] else "(v not in S)"),"color":("black" if n["alpha"] else "red")})
        for e in self.links:
            G.add_edge(e["gamma"][0],e["gamma"][1],label=e["tetha"],color=("black" if e["alpha"] else "red"))
        return G

    def draw(self):
        g=self.createNX(nx.MultiDiGraph())
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

    def draw_compact(self):
        g=self.createNX(nx.MultiDiGraph())
        pydot_graph = nx.drawing.nx_pydot.to_pydot(g)
        # render pydot by calling dot, no file saved to disk
        png_str = pydot_graph.create_png(prog='dot')
        # treat the dot output string as an image file
        temp = str(uuid.uuid4())
        with open (path+temp+'.png', 'w') as fd:
             fd.write(png_str)
        fd.close()
        return path+temp+'.png'

    def __str__(self):
        return str(self.nodes) + str(self.links)
