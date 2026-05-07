import math

def _is_num(x):
    return isinstance(x, (int, float)) and math.isfinite(x)

def path_length_km_from_graph(G, path, default_fixed_distance_km: float) -> float:
    """
    Bir path üzerindeki toplam uzunluğu (km) hesaplar.
    Eğer edge üzerinde 'distance_km' ya da 'distance_m' yoksa
    default_fixed_distance_km kullanır.
    """
    total_km = 0.0
    for u, v in zip(path[:-1], path[1:]):
        if 'distance_km' in G[u][v]:
            total_km += float(G[u][v]['distance_km'])
        elif 'distance_m' in G[u][v]:
            total_km += float(G[u][v]['distance_m']) / 1000.0
        else:
            total_km += float(default_fixed_distance_km)
    return total_km
