def calculate_esp_for_path(G, path):
    """
    Verilen path üzerinde, iç nodların swapping_prob değerlerini çarparak ESP hesaplar.

    Parametreler:
    - G (networkx.Graph): Graph
    - path (list): source-to-destination node listesi

    Dönüş:
    - esp (float): entanglement swapping probability
    """
    esp = 1.0
    # İlk ve son node hariç
    for node in path[1:-1]:
        prob = G.nodes[node].get('swapping_prob', 1.0)
        esp *= prob
    return round(esp, 6)