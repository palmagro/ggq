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
    #inputfile = open(f,'r')
    #graph = Graph("http://neo4j:pytpytpyt@localhost:7474/db/data/")
    #lines = unicodedata.normalize('NFKD', inputfile)
    #print lines[20]
    lines = lines.splitlines()
    nodes = getNodes(lines)
    links = getLinks(lines)
    inputfile.close()
    cypher = "CREATE"
    for n in nodes:
        cypher +="("+n["id"]+":"+n["type"]+"{"
        for p in n["props"]:
            cypher += p+":'"+n["props"][p]+"',"
        cypher = cypher[:-1]
        cypher += "}),"
    for l in links:
        cypher +="("+l["gamma"][0]+")-[:"+l["type"]+"]->("+l["gamma"][1]+"),"
    cypher = cypher[:-1]
    print cypher
    return cypher

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
            node["id"] = "n"+unicode(values[0])
            node["type"] = values[1].replace(",","").replace(" ","").replace("(","").replace(")","")
            node["props"] = {}
            for idx,p in enumerate(props[2:]):
                p = p.replace(" ","_").replace("(","").replace(")","").replace("'","").replace("/","")
                node["props"][p] = values[idx+2].replace("(","").replace(")","").replace("'","").replace("/","")
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
            link["gamma"] = ["n"+str(values[0]),"n"+str(values[1])]
            link["type"] = values[2].replace(" ","_")
            links.append(link)
    return links


