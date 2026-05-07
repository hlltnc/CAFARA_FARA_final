import random

def assign_swapping_probabilities(G, prob_range=(0.6, 0.95)):
    """
    Her bir node'a swapping probability değeri atar.

    Parametreler:
    - G (networkx.Graph): Grid graph
    - prob_range (tuple): (min_prob, max_prob) aralığında olmalı

    Dönüş:
    - G (networkx.Graph): Güncellenmiş node verileriyle birlikte
    """
    min_p, max_p = prob_range
    if not (0 < min_p < max_p <= 1):
        raise ValueError("Probability range must be within (0, 1] and min < max.")

    for node in G.nodes():
        G.nodes[node]['swapping_prob'] = round(random.uniform(min_p, max_p), 4)

    return G
