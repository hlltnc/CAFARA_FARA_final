


def assign_fixed_distance(G, fixed_distance):
    for u, v in G.edges():
        G[u][v]['distance'] = fixed_distance
    return G