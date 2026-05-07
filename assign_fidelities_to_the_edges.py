import random

def assign_fidelity_to_edges(G, fidelity_range=(0.8, 0.99)):
    """
    Her bir edge'e belirtilen aralıkta random bir fidelity değeri atar.

    Parametreler:
    - G (networkx.Graph): Grid graph
    - fidelity_range (tuple): (min_fidelity, max_fidelity) aralığı

    Dönüş:
    - G (networkx.Graph): Üzerine fidelity eklenmiş graph
    """
    min_fid, max_fid = fidelity_range
    if not (0 < min_fid < max_fid <= 1):
        raise ValueError("Fidelity range must be within (0, 1] and min < max.")
    
    for u, v in G.edges():
        fid = round(random.uniform(min_fid, max_fid), 4)
        G[u][v]['fidelity'] = fid

    return G, fid