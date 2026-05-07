import random

def assign_entanglement_distribution_probabilities(G, prob_range=(0.6, 0.9)):
    """
    Her bir edge'e entanglement distribution probability değeri atar.

    Parametreler:
    - G (networkx.Graph): Grid graph
    - prob_range (tuple): (min_prob, max_prob) aralığında olmalı

    Dönüş:
    - G (networkx.Graph): Güncellenmiş graph
    """
    min_p, max_p = prob_range
    if not (0 < min_p < max_p <= 1):
        raise ValueError("Probability range must be within (0, 1] and min < max.")

    for u, v in G.edges():
        G[u][v]['entanglement_prob'] = round(random.uniform(min_p, max_p), 4)

    return G