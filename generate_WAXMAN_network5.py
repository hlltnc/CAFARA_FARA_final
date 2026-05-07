# generate_WAXMAN_network.py

import math
from typing import Tuple, Optional, Literal
import numpy as np
import networkx as nx


def create_network(
    n: int,
    alpha: float = 0.45,
    beta: float = 0.20,
    *,
    # Yerleşim (node pozisyonları)
    layout: Literal["uniform", "clustered"] = "uniform",
    n_clusters: Optional[int] = None,     # clustered ise küme sayısı (None => ~sqrt(n)/2)
    cluster_spread: float = 0.06,         # clustered ise küme içi std (göreli ölçek)
    # Yoğunluk/mesh ayarı
    target_avg_degree: float = 3.0,
    ensure_connected: bool = True,
    min_degree: int = 2,                  # min derece
    # Uzun/kısa link olasılık bias’ları
    long_edge_threshold: float = 0.75,    # d > 0.75*L ise "uzun" say
    long_edge_bias: float = 1.0,          # uzun kenarlarda olasılığı (1+bias) ile çarp
    short_edge_threshold: float = 0.15,   # d < 0.15*L ise "çok kısa" say
    short_edge_bias: float = 0.0,         # kısa kenarlarda olasılığı (1+bias) ile çarp
    # Ölçek ve kenar alanları
    scale_km_per_unit: float = 3.0,      # 1 koordinat birimi kaç km?
    seed: Optional[int] = None,
    add_distance_fields: bool = True,
    add_fidelity: bool = False,
    fidelity_range: Tuple[float, float] = (0.7, 0.99),
) -> nx.Graph:
    """
    Waxman-yerleşimli, bağlantılı, seyrek mesh; kısa ve uzun link karışımı ayarlanabilir.

    ÖNEMLİ:
    - Node'lar, yan uzunluğu ~sqrt(n) olan bir koordinat karesine yerleştirilir.
      Böylece node yoğunluğu yaklaşık sabit kalır, node sayısı arttıkça fiziksel alan büyür.
    - Mesafeler: d_ij (koordinat birimi) * scale_km_per_unit → km
    """
    if n < 2:
        raise ValueError("n ≥ 2 olmalı")
    if min_degree < 1:
        raise ValueError("min_degree ≥ 1 olmalı")

    rng = np.random.default_rng(seed)

    # --- 1) Node pozisyonları (alanı n ile büyüt) ---
    # side_units: koordinat uzayında kare yan uzunluğu (birim)
    side_units = math.sqrt(n)  # n arttıkça alan ~ n olacak

    if layout == "uniform":
        # Node'ları [0, side_units] × [0, side_units] içine uniform dağıt
        pos = {
            i: (
                float(rng.random() * side_units),
                float(rng.random() * side_units),
            )
            for i in range(n)
        }
    else:  # clustered
        k = n_clusters or max(2, int(round(math.sqrt(n) / 2)))
        # Küme merkezlerini de büyük alana yay
        centers = rng.uniform(0.15 * side_units, 0.85 * side_units, size=(k, 2))
        pos = {}
        for i in range(n):
            c = rng.integers(0, k)
            # cluster_spread’i side_units ile ölçekle
            p = centers[c] + rng.normal(0.0, cluster_spread * side_units, size=2)
            p = np.clip(p, 0.0, side_units)
            pos[i] = (float(p[0]), float(p[1]))

    coords = np.array(list(pos.values()), dtype=float)

    def dij(i, j) -> float:
        """Koordinat uzaklığı (birim). Sonra km'ye çevrilecek."""
        dx = coords[i, 0] - coords[j, 0]
        dy = coords[i, 1] - coords[j, 1]
        return math.hypot(dx, dy)

    # --- 2) Tüm aday kenarlar ve L (max mesafe, birim) ---
    L = 0.0
    all_edges = []
    for i in range(n):
        for j in range(i + 1, n):
            d = dij(i, j)
            all_edges.append((i, j, d))
            if d > L:
                L = d
    L = max(L, 1e-12)

    # --- 3) MST ile başlangıç (bağlantılılık garantisi) ---
    G_complete = nx.Graph()
    G_complete.add_nodes_from(range(n))
    for i, j, d in all_edges:
        G_complete.add_edge(i, j, weight=d)

    if ensure_connected:
        T = nx.minimum_spanning_tree(G_complete, weight="weight")
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(T.edges())
    else:
        G = nx.Graph()
        G.add_nodes_from(range(n))

    # --- 4) Waxman + bias ile ek kenarlar ---
    for i, j, d in all_edges:
        if G.has_edge(i, j):
            continue
        # d ve L koordinat birimi, normalize ederek kullanıyoruz
        p = alpha * math.exp(-d / (beta * L))
        if d > long_edge_threshold * L and long_edge_bias > 0.0:
            p *= (1.0 + float(long_edge_bias))
        elif d < short_edge_threshold * L and short_edge_bias > 0.0:
            p *= (1.0 + float(short_edge_bias))
        p = max(0.0, min(1.0, p))
        if rng.random() < p:
            G.add_edge(i, j)

    # --- 5) Ortalama dereceyi hedefe yaklaştır ---
    def avg_degree(graph: nx.Graph) -> float:
        return 0.0 if graph.number_of_nodes() == 0 else \
            sum(dict(graph.degree()).values()) / graph.number_of_nodes()

    current_avg = avg_degree(G)
    if current_avg < target_avg_degree:
        needed_total_deg = target_avg_degree * n
        deficit = max(0, int(round(needed_total_deg - sum(dict(G.degree()).values()))))
        if deficit > 0:
            neighbors_sorted = {}
            for u in range(n):
                dlist = [(dij(u, v), v) for v in range(n) if v != u]
                dlist.sort()
                neighbors_sorted[u] = [v for _, v in dlist]

            added = 0
            idx = 0
            while added < deficit and idx < n * n:
                u = idx % n
                for v in neighbors_sorted[u]:
                    if u != v and not G.has_edge(u, v):
                        G.add_edge(u, v)
                        added += 1
                        break
                idx += 1

    # --- 6) Uçları kapat: min_degree garantisi ---
    if min_degree >= 2:
        max_iters = n * 3
        it = 0
        while it < max_iters:
            degree_dict = dict(G.degree())
            lows = [u for u, deg in degree_dict.items() if deg < min_degree]
            if not lows:
                break
            progressed = False
            for u in lows:
                cand = [(dij(u, v), v) for v in range(n)
                        if v != u and not G.has_edge(u, v)]
                if not cand:
                    continue
                cand.sort()
                for _, v in cand:
                    if not G.has_edge(u, v):
                        G.add_edge(u, v)
                        progressed = True
                        break
            if not progressed:
                break
            it += 1

    # --- 7) Pozisyon ve kenar alanları ---
    nx.set_node_attributes(G, pos, "pos")

    if add_distance_fields or add_fidelity:
       loF, hiF = fidelity_range

    # Tüm edge’ler için kullanmak istediğin sabit mesafe (örneğin 10 km)
       constant_dist_km = scale_km_per_unit
       constant_dist_m = constant_dist_km * 1000.0

       for u, v in G.edges():
        # İstersen gerçek geometrik mesafeyi ayrıca saklayabilirsin:
        # geom_km = dij(u, v) * scale_km_per_unit
        # G[u][v]["geom_distance_km"] = geom_km

          if add_distance_fields:
            G[u][v]["distance"] = constant_dist_km
            G[u][v]["distance_km"] = constant_dist_km
            G[u][v]["distance_m"] = constant_dist_m

          if add_fidelity:
            F = float(rng.uniform(loF, hiF))
            G[u][v]["fidelity"] = max(0.500000001, min(1.0, F))

          G[u][v]["weight"] = 1.0

    return G
