import numpy as np

def calculate_entanglement_generation_time(L, F, L_att, c_fiber=2e8):
    """
    Entanglement generation time hesaplar (denklemler [36] referans alınarak).

    Parametreler:
        L : float
            İki düğüm arasındaki mesafe (metre)
        F : float
            Fidelity değeri (0.5 < F ≤ 1)
        L_att : float
            Attenuation length (metre cinsinden), genelde L'e eşit alınır
        c_fiber : float
            Fiber içindeki ışık hızı (varsayılan: 2 × 10^8 m/s)

    Dönüş:
        ent_time : float
            Ortalama entanglement generation süresi (saniye)
    """

    # (1) η hesaplanır: η = e^(-L / L_att)
    eta = np.exp(-L / L_att)

    # (2) Başarısızlık olasılığı: P_failure = (2F - 1)^(η / (1 - η))
    exponent = eta / (1 - eta)
    Pfailure = (2 * F - 1) ** exponent

    # (3) Başarı olasılığı
    Psuccess = 1 - Pfailure

    # (4) T0: fiberdeki çift yönlü ışık süresi = 2L / c
    T0 = 2 * L / c_fiber

    # (5) Ortalama entanglement süresi
    if Psuccess > 0:
        T = T0 / Psuccess
    else:
        T = float('inf')  # başarı ihtimali 0 ise sonsuz zaman gerekir

    return T
