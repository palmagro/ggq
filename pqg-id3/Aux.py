def recordToList(record,field):
    l = []
    for r in record:
        if r[field]:
            l.append(r[field])
    return l

