import numpy as np
from final_fidelity_after_purification import final_fidelity_after_purification




def compute_path_final_fidelity(G, path, alpha, successful_purification_rounds, default_distance_km, default_F_init=0.9):
    edge_final_fidelities = []

    for u, v in zip(path[:-1], path[1:]):
        F_edge_init = G[u][v].get("fidelity", default_F_init)

        if "distance_km" in G[u][v]:
            L_edge_km = float(G[u][v]["distance_km"])
        elif "distance_m" in G[u][v]:
            L_edge_km = float(G[u][v]["distance_m"]) / 1000.0
        else:
            L_edge_km = float(default_distance_km)

        F_edge_after_loss = 0.5 + (F_edge_init - 0.5) * np.exp(-alpha * L_edge_km)

        F_edge_final = final_fidelity_after_purification(F_edge_after_loss, successful_purification_rounds)

        edge_final_fidelities.append(F_edge_final)

    if not edge_final_fidelities:
        return 0.0, []

    F_final_path = float(np.prod(edge_final_fidelities))

    if F_final_path < 0.0:
        F_final_path = 0.0
    if F_final_path > 1.0:
        F_final_path = 1.0

    return F_final_path, edge_final_fidelities
