def calculate_usable_capacity_for_path(G, path):
    # 1. Ara düğümleri al
    intermediate_nodes = path[1:-1]
    
    # 2. Swapping olasılıklarını carp
    swapping_factor = 1.0
    print(f"\nIntermediate nodes for path {path}: {intermediate_nodes}")
    for node in intermediate_nodes:
        swapping_prob = G.nodes[node].get('swapping_prob')
        print(f"  Node {node} swapping_prob = {swapping_prob}")
        swapping_factor *= swapping_prob
        
    # 3. Path üzerindeki edge’lerin kapasitesine bak
    edge_capacities = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if G.has_edge(u, v):
            edge_capacities.append(G[u][v].get('capacity', 0))
        elif G.has_edge(v, u):  # yönsüz ağlar için
            edge_capacities.append(G[v][u].get('capacity', 0))

    if not edge_capacities:
        print("  Warning: No valid edges in path.")
        return 0

    min_capacity = min(edge_capacities)

    # 4. Swapping ile usable capacity’yi hesapla
    usable_capacity = min_capacity * swapping_factor
    print(f"  → min_capacity = {min_capacity}, swapping_factor = {swapping_factor:.4f}, usable_capacity = {usable_capacity:.4f}")
    return usable_capacity


#simdi required demandi bulmamiz gerek
