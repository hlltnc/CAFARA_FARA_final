


import math



def compute_required_bell_pairs(demand, purification_rounds, G, path):
    """
    Bir request için gerekli toplam Bell pair sayısını hesaplar.
    
    Hesaplama:
    - Intermediate node'ların swapping_prob (ESP) değerleri çarpılır.
    - purification_rounds == 0 ise:
          ceil(demand / ESP_product)
    - purification_rounds > 0 ise:
          demand * ceil((2 ** purification_rounds) / ESP_product)

    Args:
        demand (int or float): Request için gerekli qubit sayısı.
        purification_rounds (int): Gerekli purification round sayısı.
        G (networkx.Graph): Node'larda 'swapping_prob' attribute'u bulunan graph.
        path (list): Request'in geçtiği path. Örn: [src, n1, n2, dst]

    Returns:
        int or None: Toplam gerekli Bell pair sayısı.
                     Eğer purification yapılamıyorsa None döner.
    """
    if purification_rounds is None:
        return None

    if demand < 0:
        raise ValueError("demand must be non-negative")

    if path is None or len(path) < 2:
        raise ValueError("path en az source ve destination içermelidir")

    # Intermediate node'lar: source ve destination hariç
    intermediate_nodes = path[1:-1]

    # ESP çarpımı
    esp_product = 1.0
    for node in intermediate_nodes:
        if 'swapping_prob' not in G.nodes[node]:
            raise KeyError(f"Node {node} için 'swapping_prob' tanımlı değil.")
        
        esp = G.nodes[node]['swapping_prob']
        if esp <= 0 or esp > 1:
            raise ValueError(f"Node {node} için swapping_prob geçersiz: {esp}")
        
        esp_product *= esp

    # Intermediate node yoksa çarpım 1 kalır
    if purification_rounds == 0:
        return math.ceil(demand / esp_product)

    required_bell_pairs_for_purification = 2 ** purification_rounds

    per_qubit_required = math.ceil(required_bell_pairs_for_purification / esp_product)
    required_bell_pairs_total = demand * per_qubit_required

    return required_bell_pairs_total




 