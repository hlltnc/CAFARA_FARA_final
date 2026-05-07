import networkx as nx
from typing import Dict, Tuple

def assign_capacity_from_values(
    G: nx.Graph,
    edge_values: Dict[Tuple[int, int], int],
    *,
    field_name: str = 'capacities'
) -> nx.Graph:
    """
    edge_values: {(u,v): val, ...} sözlüğünü grafiğe yazar.
    (u,v) anahtarını (min,max) ile normalize ederek hem (u,v) hem (v,u) eşleşmelerini yakalar.
    """
    # Anahtarları normalize edilmiş kopya oluştur
    norm_map = {}
    for (a, b), val in edge_values.items():
        u, v = (a, b) if a <= b else (b, a)
        norm_map[(u, v)] = val

    # Grafikteki her edge için değer ata (normalize ederek bak)
    for u, v in G.edges():
        a, b = (u, v) if u <= v else (v, u)
        if (a, b) in norm_map:
            G[u][v][field_name] = norm_map[(a, b)]
        # yoksa dokunma (önceden assign_filtered_capacities yazdıysa o kalsın)

    return G
