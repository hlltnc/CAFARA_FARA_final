def calculate_swapping_time(G, path, c_fiber=2e8):
    """
    Bir path için toplam swapping süresini hesaplar.
    Swapping işlemi her iç düğümde gerçekleşir.

    Parametreler:
    - G: networkx graph
    - path: node dizisi (örn: [0, 2, 3])
    - c_fiber: fiberdeki ışık hızı (varsayılan 2×10^8 m/s)

    Dönüş:
    - total_swapping_time: toplam swapping süresi (saniye)
    """

    total_time = 0
    for i in range(1, len(path) - 1):
        u = path[i - 1]
        v = path[i + 1]

        # u → v arasındaki toplam mesafeyi tahmin et (iki kenarın ortalaması da olur)
        d = G[path[i - 1]][path[i]]["distance"]
        L = d*1000

        t_swap = L / c_fiber
        total_time += t_swap

    return total_time