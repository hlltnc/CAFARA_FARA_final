from calculate_entanglement_generation_time_from_graph_waxman import calculate_entanglement_generation_time_from_graph

def calculate_total_entanglement_time(G, path, L_att):
    total_time = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        t = calculate_entanglement_generation_time_from_graph(G, (u, v), L_att)  # <-- tuple ver
        total_time += t
    return total_time