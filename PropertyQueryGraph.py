class PropertyQueryGraph:
    nodes = []
    links = []
    def __init__(self):
        self.nodes = []
        self.links = []
    def addNode(self,label,alpha,tetha,fixed):
        self.nodes.append({"label":label,"alpha":alpha,"tetha":tetha,"fixed":fixed})
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
    def __str__(self):
        return str(self.nodes) + str(self.links)
