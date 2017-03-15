def recordToList(record,field):
    l = []
    for r in record:
        if r[field]:
            l.append(r[field])
    return l

def NLGtoCypher(f):
    inputfile = open(f)
    for line in inputfile:
        print line
    inputfile.close()
