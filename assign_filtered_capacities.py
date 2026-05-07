import networkx as nx
import random

def assign_filtered_capacities(G, freq_for_capacity, CAPACITY_RANGE, elementary_entanglement_generation_rate):
    """
    Her edge için:
      - [lo, hi] aralığından freq_for_capacity adet uniform integer üret
      - p_edge = edge['entanglement_prob'] (varsa) yoksa global p
      - capacity_threshold = hi * p_edge
      - val < threshold olanları filtrele
      - sonucu G[u][v]['capacities'] listesi olarak yaz
    Grid/Waxman fark etmez; create_network ile üretilen G için doğrudan çalışır.
    """
    # Aralıkları güvenli al
    lo, hi = CAPACITY_RANGE
    if lo > hi:
        lo, hi = hi, lo

    for u, v in G.edges():
        # Kenara özel olasılık (varsa), yoksa global p
        try:
            p_edge = float(G[u][v].get("entanglement_prob", elementary_entanglement_generation_rate))
        except Exception:
            p_edge = float(elementary_entanglement_generation_rate)
        # [0,1] sıkıştır
        if p_edge < 0.0: p_edge = 0.0
        if p_edge > 1.0: p_edge = 1.0

        capacity_threshold = hi * p_edge  # eşik

        # Uniform örnekler ve filtre
        capacity_values = [random.randint(lo, hi) for _ in range(freq_for_capacity)]
        filtered_capacities = [val for val in capacity_values if val < capacity_threshold]

        # Listeyi yaz
        G[u][v]['capacities'] = filtered_capacities

    return G  # Mutlaka G'yi return et
