# -*- coding: utf-8 -*-
'''
This is the file that handles cjl's requests.
'''

import networkx as nx

def record_line_graph(from_filepath, to_filepath):
    '''
        Record the line graph's edges and original graph's nodes relationship.
        
        parametres:
            from_filepath: the file where the original graph is recorded
            to_filepath: the file where the line graph and its relation are recorded
    '''
    f = open(from_filepath)
    lines = f.readlines()
    f.close()
    edges = [item.strip().split() for item in lines if item.strip()]
    f = open(to_filepath, 'wb')
    count = 0
    for edge in edges:
        f.write('%i:%s,%s,%s\r\n' %(count, edge[0], edge[1], edge[2]))
        count += 1
    f.close()
    
def line_graph(from_filepath, to_filepath=None, weight=None):
    '''
        Compute a graph's line graph. Whether it's weighted or not.
        
        parametres:
            from_filepath: the file where the original graph is recorded
            to_filepath: the file where the line graph and its relation are recorded
            weighted: whether the original graph is with weight.
                      If it is, compute the line graph's weighted.
        
        return:
            the line graph: L.
            But L is not a weighted graph.
            If you need to give L weights, you need to define a good way to give weights.
    '''
    f = open(from_filepath)
    edges = [item.split() for item in f.readlines() if item.strip()]
    f.close()
    
    for edge in edges:
        edge[0] = int(edge[0].strip())
        edge[1] = int(edge[1].strip())
        edge[2] = float(edge[2].strip())
    g = nx.Graph()
    g.add_weighted_edges_from(edges)
    
    L = nx.line_graph(g)
    
    # if it is not a weighted graph
    if not weight:
        return L
    
    nodes = L.nodes()
    length = len(nodes)
    for i in xrange(0, length-1, 1):
        for j in xrange(i+1, length, 1):
            try:
                L[nodes[i]][nodes[j]]['weight'] = g.get_edge_data(*nodes[i])['weight']/(g.degree(nodes[i][0])+g.degree(nodes[i][1])-2)  + g.get_edge_data(*nodes[j])['weight']/(g.degree(nodes[j][0])+g.degree(nodes[j][1])-2)
            except:
                pass
            #print g.get_edge_data(*nodes[i])['weight']
    
    return L
    
def pairs_closer_than(g, d=2, weight=None):
    '''
        Compute all the pairs of nodes whose distance is less than parametre d.
        
        parametres:
            g: the graph
            d: the distance specified
            weighted: if the graph is weighted or not
        
        return:
            ...
    '''
    #shortest length of the graph
    shortest_length = nx.shortest_path_length(g, weight=weight)
    
    nodes = g.nodes()
    n = len(nodes)
    dict_less_d = {}
    
    #set_less_d = [set() for i in range(n)]
    
    #if two nodes' distance is less than d, record each node into the other's set
    for i in range(n-1):
        for j in range(i+1, n):
            if shortest_length[nodes[i]][nodes[j]] <= d:
                if not dict_less_d.has_key(nodes[i]):
                    dict_less_d[nodes[i]] = set([nodes[j]])
                else:
                    dict_less_d[nodes[i]].add(nodes[j])
                if not dict_less_d.has_key(nodes[j]):
                    dict_less_d[nodes[j]] = set([nodes[i]])
                else:
                    dict_less_d[nodes[j]].add(nodes[i])
                
    # kick out the nodes in one node's set
    dict_kick_out = {}
    
    for node in dict_less_d:
        # init the kick_out item indexed by node
        dict_kick_out[node] = set()
        lst = list(dict_less_d[node])
        length = len(lst)
        for j in range(0, length-1):
            for k in range(j+1, length):
                # If j is not in the set corresponding to k, k is also not in the set corresponding to j
                # So this 'if' statement only needs to checked once.
                if lst[j] not in dict_less_d[lst[k]]:
                    ''' This isn't used.
                    # If node[j] has more weight with the node's set than node[k] is, the remove node[j],
                    # else if node[k] has more than node[j] remove node[k], otherwise remove one of them randomly.
                    try:
                        lenj = g[node][lst[j]]
                    except:
                        lenj = 0
                    for item in dict_less_d[node]:
                        try:
                            lenj += g[item][lst[j]]
                        except:
                            pass
                    
                    try:
                        lenk = g[node][lst[k]]
                    except:
                        lenk = 0
                    for item in dict_less_d[node]:
                        try:
                            lenk += g[item][lst[k]]
                        except:
                            pass
                    '''
                    
                    
                    lenj = len(dict_less_d[node].intersection(dict_less_d[lst[j]]))
                    lenk = len(dict_less_d[node].intersection(dict_less_d[lst[k]]))
                    if lenj > lenk:
                        dict_kick_out[node].add(lst[k])
                    elif lenk > lenj:
                        dict_kick_out[node].add(lst[j])
                    else:
                        "Kick j or k randomly."
                        from random import random
                        if random() >= 0.5:
                            dict_kick_out[node].add(lst[k])
                        else:
                            dict_kick_out[node].add(lst[j])
    
    for node in dict_less_d:
        dict_less_d[node].difference_update(dict_kick_out[node])
    return dict_less_d

def partition(g, dict_less_d):
    '''
        After we get the dict in which all the nodes is closer than d,
        we partition the graph's nodes into serval sets, each represents a cluster.
        
        Parametres:
                    g: the graph we handle
                    dict_less_d: dict closer than d
        
        Return:
                    a list representing the clusters.
    '''
    # Contruct the node group, each node is in at least one group.
    # Remember that list nodes and list groups are corresponding to each other.
    # That means groups[i] is the set of nodes in which the nodes' distances between
    # them and nodes[i] are less than d.
    # And also size is with the groups and nodes too.
    nodes = g.nodes()
    groups = []
    for node in nodes:
        groups.append([node])
        if dict_less_d.has_key(node):
            groups[-1].extend(dict_less_d[node])
    
    
    # A list recording the partition result.
    partition = []
    
    # Find the largest length of the set.
    # Add this set to result, after that remove all nodes of this set in other sets.
    # After all the removal, groups will be empty, then break the while loop.
    while groups:
        size = [len(i) for i in groups]
        m = max(size)
        if m == 0:
            break
        idx = size.index(m)
        partition.append(groups[idx])
        to_remove = groups[idx]
        groups.pop(idx)
        for item in to_remove:
            for s in groups:
                if item in s:
                    s.remove(item)
    return partition

def merge_partition(g, partition, size=1, weight=None):
    '''
        Merge the clusters of size less than the size into the one which has the
        largest sum of weight.
        
        Parametres:
                    g: the graph we handle
                    partition: partition of the graph g
                    size: ####
        
        Return:
                    a list representing the clusters after merge the small ones.
    '''
    less_than_size = []
    set_size = []
    for i in partition:
        if len(i)<=size:
            less_than_size.append(i)
            set_size.append(len(i))
    if len(less_than_size)==0:
        return partition
    
    while less_than_size:
        # Each time, we check the smallest length of the less_than_size.
        # Remember to remove the one with the smallest size.
        idx = set_size.index(min(set_size))
        i = less_than_size[idx]
        
    #for i in less_than_size:
    #    if i in removed:
    #        less_than_size.remove(i)
    #        continue
        mij = {}
        for j in partition:
            if i is not j:
                # if i and j is connected with edges m=0, otherwise m=-1.
                m = 0 if compute_cij(i, j, g)>0 else -1
                if m==0:
                    if weight:
                        # compute the m value. If i has one node, m = wij/cij, else m = wij/(cij*(wii+wjj))
                        if len(i)==1 or len(j)==1:
                            m = compute_wij(i, j, g)*1.0/compute_cij(i, j, g)
                        else:
                            m = compute_wij(i, j, g)*1.0/(compute_cij(i, j, g)*(compute_wij(i, i, g)+compute_wij(j, j, g)))
                    else:
                        # compute the m value. If i has one node, m=cij/cjj, else m = cij/(cii+cjj)
                        # remember that in this unweighted case, if i has one node, j would have more than one node.
                        '''
                        cij = compute_cij(i, j, g)*1.0
                        cii = compute_cij(i, i, g)
                        cjj = compute_cij(j, j, g)
                        m = cij/(cii+cjj)
                        '''
                        m = compute_cij(i, j, g)*1.0/(compute_cij(i, i, g)+compute_cij(j, j, g))
                    
                    if mij.has_key(m):
                        mij[m].append(j)
                    else:
                        mij[m] = [j]
        # get the max walue of mij, in order to merge cluster i to the one.
        m = max(mij.keys())
        
        # modify the less_than_size and set_size
        # firstly we remove i from less_than_size and its size from set_size
        less_than_size.remove(i)
        set_size.pop(idx)
        # secondly, check if the cluster that i merge into is in less_than_size or not
        if mij[m][0] in less_than_size:
            # if it is in the less_than_size, find the index of the cluster and extend it with i
            # then check the cluster to see if its size is larger than size, if it is, remove it from less_than_size
            idx = less_than_size.index(mij[m][0])
            less_than_size[idx].extend(i)
            if len(less_than_size[idx])>size:
                less_than_size.pop(idx)
                set_size.pop(idx)
            partition.remove(i)
        else:
            # modify the partition
            partition[partition.index(mij[m][0])].extend(i)
            partition.remove(i)
            print 'len(partition)', partition
        
    return partition


def compute_wij(i, j, g):
    '''
        Compute the weighted g's cluster i and cluster j's sum of weights.
        If i is j, return wii, and if i has only one node, return 0.
        Otherwise return wij.
        
        Return
                The sum of the weights of the edges between i and j.
                If i is j, return the inner sum of the weights, and if i has only
                one node, return 0.
    '''
    wij = 0
    # Check if i is j, if it is true, 
    if i is j:
        # If i is j and length of i is 1, then cluster i has only node. Then wii=0,and return 0.
        length = len(i)
        for m in range(length-1):
            for n in range(m+1, length):
                try:
                    wij += g[node_i][node_j]['weight']
                except:
                    pass
    else:   # Otherwise, i is not j. Then we return wij
        for node_i in i:
            for node_j in j:
                try:
                    wij += g[node_i][node_j]['weight']
                except:
                    pass
    return wij
    
    
def compute_cij(i, j, g, weight=None):
    '''
        Compute the number of connecting edges between the cluster i and cluster j.
        
        Return:
                The number between cluster i and j.
                If i and j does not have a link or i is j and i has only one node,
                then cij=0.
    '''
    cij = 0
    # Check if i is j.
    if i is j:  # If i is j.
        # If i has only one node, then cij=0.
        length = len(i)
        for m in range(length-1):
            for n in range(m+1, length):
                if g[i[m]].has_key(i[n]):
                    cij += 1
    else:   # If i is not j.
        for node_i in i:
            for node_j in j:
                if g[node_i].has_key(node_j):
                    cij += 1
    return cij

def test():
    L = line_graph('D:/protein-structure-1 .txt', 'D:/protein-structure-2 .txt', True)
    print pairs_closer_than(L, d=1, weight=True)

def test_weighted_graph():
    L = line_graph('D:/test_graph.txt', weight=True)
    dict_less_d = pairs_closer_than(L, d=21, weight=True)
    print 'dict_less_d:', dict_less_d
    p = partition(L, dict_less_d)
    print 'partition:', p
    print 'last:', merge_partition(L, p, size=1, weight=True)
    
def test_unweighted_graph():
    L = line_graph('D:/test_graph.txt')
    print L.edges()
    dict_less_d = pairs_closer_than(L, d=2)
    print 'dict_less_d:', dict_less_d
    
    p = partition(L, dict_less_d)
    print 'partition:', p
    
    print 'last:', merge_partition(L, p, size=1)
    

if __name__ == '__main__':
    #record_line_graph_edge_node_relation('D:/protein-structure-1 .txt', 'D:/protein-structure-2 .txt')
    #line_graph('D:/protein-structure-1 .txt', 'D:/protein-structure-2 .txt')
    test_unweighted_graph()