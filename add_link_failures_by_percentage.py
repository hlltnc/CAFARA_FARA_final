import random

def add_link_failures_by_percentage(G, failure_percentage, fail_fidelity):
    """
    Network'teki linklerin %X kadarına failure uygular.
    
    Parameters:
        G: networkx Graph (directed veya undirected)
        failure_percentage: 0.1 = %10 link failure
        min_fidelity: failure olan linklerin alacağı fidelity (default: 0.5)

    Returns:
        G: güncellenmiş grafik
        failed_edges: bozulmuş edge'lerin listesi
    """
    edge_list = list(G.edges())
    total_links = len(edge_list)

    # Kaç tane link bozulacak
    num_failures = int(total_links * failure_percentage)
    if num_failures == 0:
     return G, []  # hiç bozulma yok, direkt geri dön
    #print(num_failures)
    # Rastgele bozulacak linkleri seç
    failed_edges = random.sample(edge_list, num_failures)

    for u, v in failed_edges:
        G[u][v]["fidelity"] = fail_fidelity
        if not G.is_directed() and G.has_edge(v, u):
            G[v][u]["fidelity"] = fail_fidelity

    return G, failed_edges
