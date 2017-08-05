import codecs
import re
import unicodedata
from py2neo import Graph
def recordToList(record,field):
    l = []
    for r in record:
        if r[field]:
            l.append(r[field])
    return l

def NLGtoCypher(f):
    inputfile = codecs.open(f, "r", "utf-8")
    lines = inputfile.read()
    lines.replace(u'\u0301',"")
    #inputfile = open(f,'r')
    graph = Graph("http://neo4j:pytpytpyt@church.cs.us.es:7474/db/data/")
    lines = unicodedata.normalize('NFKD', lines)
    #print lines[20]
    lines = lines.splitlines()
    nodes = getNodes(lines)
    links = getLinks(lines)
    inputfile.close()
    print "NODOS LISTOS"
    for l in links:
        cypher = "MATCH (a{idx:'"+l["gamma"][0][1:]+"'}),(b{idx:'"+l["gamma"][1][1:]+"'})"
        cypher += "MERGE (a)-[r:"+l["type"]+"]->(b)"
        print cypher
        result = graph.run(cypher)
    #cypher = cypher[:-1]
    #print cypher
    #result = graph.run(cypher)
    #print cypher
    #return cypher

def filterIds(s):
    return s.replace(",","").replace(" ","").replace("(","").replace(")","").replace("-","_").replace("/","_").replace(".","_").replace("'","_").replace("|","_").replace("?","_").replace(":","_")

def noComment(line):
    return line[0] != "%"

def getNodes(lines):
    nodes = []
    group_nodes = []
    pair = []
    for idx,l in enumerate(lines):
        if l == "<Nodes>":
            pair.append(idx)
        if l == "<EndNodes>":
            pair.append(idx)
            group_nodes.append(pair)
            pair = []
    for group in group_nodes:
        props = re.findall('"([^"]*)"',lines[group[0]+1])
        for i in range(group[0]+2,group[1]):
            values = re.findall('"([^"]*)"',lines[i])
            node = {}
            node["id"] = "n"+unicode(filterIds(values[0]))
            node["type"] = values[1].replace(",","").replace(" ","").replace("(","").replace(")","")
            node["props"] = {"idx":unicode(filterIds(values[0]))}
            for idx,p in enumerate(props[2:]):
                p = p.replace(" ","_").replace("(","").replace(")","").replace("'","").replace("/","").replace('"',"_")
                node["props"][p] = values[idx+2].replace("(","").replace(")","").replace("'","").replace("/","").replace('"',"_")
            nodes.append(node)
    return nodes

def getLinks(lines):
    links = []
    group_links = []
    pair = []
    for idx,l in enumerate(lines):
        if l == "<Edges>":
            pair.append(idx)
        if l == "<EndEdges>":
            pair.append(idx)
            group_links.append(pair)
            pair = []
    for group in group_links:
        for i in range(group[0]+2,group[1]):
            values = re.findall('"([^"]*)"',lines[i])
            link = {}
            link["gamma"] = ["n"+filterIds(values[0]),"n"+filterIds(values[1])]
            link["type"] = values[2].replace(" ","_")
            links.append(link)
    return links

class Cont(object):
    def __init__(self):
        self.cont = 1
