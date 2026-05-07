from math import exp, ceil  # exp: üstel fonksiyon; ceil: üst tamsayı

# --- Fiziksel sabitler / yardımcılar ---

def p_local(p_ht, nu_h, nu_t):
    # Yerel dolanıklık olasılığı p = p_ht * nu_h * nu_t  (Eş. (1))
    return p_ht * nu_h * nu_t

def link_success_prob(p, nu_o, d_ij, L0):
    # p_ij = (1/2) * nu_o * p^2 * e^{-d_ij/L0}  (Eş. (2))
    return 0.5 * nu_o * (p ** 2) * exp(-d_ij / L0)

def tau_ij(tau_t, tau_o, tau_c_ij, d_ij, c_f):
    # τ_ij = τ_t + τ_o + τ_c_ij + d/(2 c_f)  (Eş. (5))
    return tau_t + tau_o + tau_c_ij + d_ij / (2 * c_f)

def T_success_ij(tau_p, tau_h, tau_ij_val, tau_gen=0.0):
    # T^s_ij = τ_p + max{τ_h, τ_ij} + tau_gen  (Eş. (4) + opsiyonel jenerasyon süresi)
    return tau_p + max(tau_h, tau_ij_val) + tau_gen

def T_fail_ij(tau_p, tau_h, tau_ij_val, tau_d, tau_gen=0.0):
    # T^f_ij = τ_p + max{τ_h, τ_ij, τ_d} + tau_gen  (Eş. (6) + opsiyonel jenerasyon süresi)
    return tau_p + max(tau_h, tau_ij_val, tau_d) + tau_gen

def T_avg_link(p_ij, T_s, T_f):
    # T_ij = (p̄ T^f + p T^s) / p  (Eş. (7))
    pbar = 1 - p_ij
    return (pbar * T_f + p_ij * T_s) / p_ij

def R_link(T_ch, tau_ij_val, T_ij):
    # R_ij(T_ch) = 0  if T_ch < τ_ij  else 1/T_ij  (Eş. (8))
    if T_ch < tau_ij_val:
        return 0.0
    return 1.0 / T_ij

# --- Uçtan-uca (route) hesapları ---

def T_c_route(tau_c_list, l, m):
    # T^c_{R_{σ_l,σ_m}} = Σ τ^c_{σ_i,σ_{i+1}}  (Eş. (10) tanımı)
    return sum(tau_c_list[i] for i in range(l, m))

def T_route(T_links, tau_c_list, tau_a, nu_a, l, m):
    # Özyinelemeli uçtan-uca beklenen süre  (Eş. (10))
    if m == l + 1:
        return T_links[l]
    k = ceil((m + l) / 2)
    left = T_route(T_links, tau_c_list, tau_a, nu_a, l, k)
    right = T_route(T_links, tau_c_list, tau_a, nu_a, k, m)
    comm = max(T_c_route(tau_c_list, l, k), T_c_route(tau_c_list, k, m))
    return (max(left, right) + tau_a + comm) / nu_a

def tau_route(Ts_links, tau_c_list, tau_a, l, m):
    # Minimal gerekli saklama zamanı  (Eş. (12))
    if m == l + 1:
        return Ts_links[l]
    k = ceil((m + l) / 2)
    left = tau_route(Ts_links, tau_c_list, tau_a, l, k)
    right = tau_route(Ts_links, tau_c_list, tau_a, k, m)
    comm = max(T_c_route(tau_c_list, l, k), T_c_route(tau_c_list, k, m))
    return max(left, right) + tau_a + comm

def R_route(T_ch, T_R, tau_R, Ts_links, taus_links):
    # R_R(T_ch) = 0 if T_ch < τ_R - min_l{ T^s_l - τ_l }  else 1/T_R  (Eş. (11))
    margin = min(Ts - tau for Ts, tau in zip(Ts_links, taus_links))
    if T_ch < (tau_R - margin):
        return 0.0
    return 1.0 / T_R

# --- Üst seviye: tek link ve rota için hesaplayıcılar ---

def compute_link_rate(params):
    """
    params sözlüğünde beklenen anahtarlar:
      p_ht, nu_h, nu_t, nu_o, L0, d_ij, c_f,
      tau_p, tau_h, tau_t, tau_o, tau_c_ij, tau_d, T_ch,
      (opsiyonel) tau_gen
    """
    tau_gen = float(params.get('tau_gen', 0.0))

    p = p_local(params['p_ht'], params['nu_h'], params['nu_t'])               # (1)
    p_ij = link_success_prob(p, params['nu_o'], params['d_ij'], params['L0']) # (2)
    tauij = tau_ij(params['tau_t'], params['tau_o'], params['tau_c_ij'],
                   params['d_ij'], params['c_f'])                             # (5)
    T_s = T_success_ij(params['tau_p'], params['tau_h'], tauij, tau_gen)      # (4)
    T_f = T_fail_ij(params['tau_p'], params['tau_h'], tauij, params['tau_d'], tau_gen)  # (6)
    T_avg = T_avg_link(p_ij, T_s, T_f)                                        # (7)
    R = R_link(params['T_ch'], tauij, T_avg)                                   # (8)

    return {
        'p': p, 'p_ij': p_ij, 'tau_ij': tauij,
        'T_s': T_s, 'T_f': T_f, 'T_avg': T_avg, 'R_ij': R
    }

def compute_route_rate(link_params_list, tau_a, nu_a, T_ch):
    """
    link_params_list: rota üzerindeki her link için param sözlükleri (compute_link_rate ile uyumlu)
    tau_a: atomik BSM süresi
    nu_a: atomik BSM verimi
    T_ch: bellek koherens zamanı
    """
    # Tüm linkler için ara büyüklükleri hesapla
    link_stats = [compute_link_rate(p) for p in link_params_list]
    T_links  = [ls['T_avg'] for ls in link_stats]
    Ts_links = [ls['T_s']   for ls in link_stats]
    taus_links = [ls['tau_ij'] for ls in link_stats]
    tau_c_list = [p['tau_c_ij'] for p in link_params_list]

    # Uçtan-uca süre ve gerekli saklama zamanı
    T_R = T_route(T_links, tau_c_list, tau_a, nu_a, 0, len(T_links))
    tau_R = tau_route(Ts_links, tau_c_list, tau_a, 0, len(T_links))

    # Uçtan-uca oran
    R_R = R_route(T_ch, T_R, tau_R, Ts_links, taus_links)
    return {'links': link_stats, 'T_R': T_R, 'tau_R': tau_R, 'R_route': R_R}

# --- Yardımcı: gerçek mesafe ve L0'ı doğrudan içeri ver ---

def build_link_params(common, d_ij, L0=None, tau_c_ij=None, tau_gen=None):
    """
    common: ortak parametre sözlüğü (p_ht, nu_h, nu_t, nu_o, L0, c_f, tau_p, tau_h, tau_t, tau_o, tau_d, T_ch)
    d_ij: iki node arası gerçek mesafe (metre)
    L0: (opsiyonel) fiber zayıflama uzunluğu (metre) -> verilirse common['L0'] üzerine yazılır
    tau_c_ij: (opsiyonel) klasik iletişim gecikmesi (s). Vermezsen ~ d/(2 c_f) olarak hesaplanır.
    tau_gen: (opsiyonel) entanglement generation time (s) -> verilirse deneme başına ek süre olarak kullanılır.
    """
    params = dict(common)
    params['d_ij'] = float(d_ij)
    if L0 is not None:
        params['L0'] = float(L0)
    if tau_c_ij is None:
        params['tau_c_ij'] = params['d_ij'] / (2 * params['c_f'])
    else:
        params['tau_c_ij'] = float(tau_c_ij)
    if tau_gen is not None:
        params['tau_gen'] = float(tau_gen)
    return params
