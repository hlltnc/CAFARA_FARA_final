import networkx as nx
from copy import deepcopy

def get_all_edge_disjoint_paths(G, request):
    """
    Belirli bir request için edge-disjoint path'leri bulur.
    
    Input:
        G: networkx graph
        request: DataFrame satırı (örneğin df_sorted.iloc[i])
                 'source' ve 'destination' sütunlarını içermeli
                 
    Output:
        disjoint_paths: list of lists, her biri bir path
    """
    source = request['source']
    target = request['destination']
    G_copy = deepcopy(G)
    disjoint_paths = []

    while True:
        try:
            path = nx.shortest_path(G_copy, source=source, target=target)
            disjoint_paths.append(path)

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if G_copy.has_edge(u, v):
                    G_copy.remove_edge(u, v)
                elif G_copy.has_edge(v, u):  # Yönsüz graph durumunda
                    G_copy.remove_edge(v, u)
        except nx.NetworkXNoPath:
            break

    return disjoint_paths
