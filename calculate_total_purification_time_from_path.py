

from calculate_purification_time_full import calculate_purification_time_full
from calculate_purification_time_full import calculate_Zn
from calculate_purification_time_full import comb

def calculate_total_purification_time_from_path(G, path, rounds, F_initial, L_att, c_fiber=2e8):
    """
    Bir path üzerindeki tüm edge'ler için purification time hesaplar.

    Parametreler:
        G: networkx graph
        path: list of nodes (örneğin: [0, 2, 3])
        rounds: purification round sayısı
        F_initial: başlangıçta edge'e atanmış fidelity
        L_att: attenuation length (metre cinsinden)

    Dönüş:
        toplam purification süresi (saniye)
    """
    if rounds is None or rounds == 0:
        return 0.0

    total_t_purif = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        L_km = G[u][v]["distance"]
        L = L_km * 1000  # metre cinsine çevir
        t_purif = calculate_purification_time_full(F_initial, L, L_att, rounds, c_fiber)
        total_t_purif += t_purif

    return total_t_purif