import numpy as np
import pandas as pd
from itertools import product


# --- FE2E (sabit C0 varsayımı ile) ---
def compute_FE2E_updated(C_rel_ent, M, X, kappa, alpha, L, anj=1.0, tau_mode="alt", fallback=0.5):
    C = np.asarray(C_rel_ent, dtype=float)
    C_safe = np.clip(C, 1e-12, 1.0)
    if tau_mode == "alt":
        tau = -np.log(C_safe / 1.045) / 0.634
    else:
        tau = (-np.log(C_safe / 1.0762) / 1.0392) ** (1.0 / 0.5673)
    F_l = 0.5 + 0.5 * np.exp(-8.0 * kappa * tau - alpha * L)
    term1 = F_l**2 + (1 - F_l)**2
    term2 = (1 - (1 - term1)**M) * (F_l**2 / (F_l**2 + (1 - F_l)**2))
    FE2E = term2**(X-1)
    if np.isscalar(FE2E):
        FE2E = FE2E if np.isfinite(FE2E) else fallback
    else:
        FE2E = np.where(np.isfinite(FE2E), FE2E, fallback)
    if M == 0:
        FE2E = F_l**(X-1)
    if X == 1:
        FE2E = F_l
    return FE2E



# -- C_rel: 'other' model + fiziksel normalizasyon + güvenlik kırpması --
def compute_C_rel(total_time):
    
    total_time = float(total_time)
    C_raw = 1.0762 * np.exp(-1.0392 * (total_time ** 0.5673))
    C_rel_norm = C_raw / 1.0762                 # normalize: C(0)=1
    C_rel = float(np.clip(C_rel_norm, 1e-12, 0.99))
    return C_rel

# -- Senin FE2E fonksiyonun AYNI kalıyor. Burada sadece çağıracağız. --
# def compute_FE2E_updated(...):  # aynen sende var

def build_Creal_forward_lookup(
    total_time_list,   # C0 yerine total_time dışarıdan geliyor
    L_list_km,
    M_list,
    X_list,
    *,
    kappa=0.2,
    alpha=0.02
) -> pd.DataFrame:
    rows = []
    for total_time, L, M, X in product(total_time_list, L_list_km, M_list, X_list):
        C_rel = compute_C_rel(total_time)
        FE2E  = compute_FE2E_updated(
            C_rel, M, X, kappa, alpha, L,
            tau_mode="other"   # TUTARLILIK: C_rel 'other' modelinden geldi
        )
        rows.append({
            "total_time": float(total_time),
            "L_km": float(L),
            "M": int(M),
            "X": int(X),
            "C_real": float(C_rel),
            "FE2E": float(FE2E),
        })
    return pd.DataFrame(rows)

# Örnek kullanım + dosya adı aynı
if __name__ == "__main__":
    total_time_list = np.round(np.arange(0.0, 5.0 + 1e-9, 0.1), 3)
    L_list_km = np.linspace(0.0, 200.0, 201)
    M_list = np.arange(0, 31)
    X_list = np.arange(1, 31)

    df_fwd = build_Creal_forward_lookup(
        total_time_list, L_list_km, M_list, X_list,
        kappa=0.2, alpha=0.02
    )

    out_csv = "FE2E_forward_lookup.csv"
    df_fwd.to_csv(out_csv, index=False)
    print(f"[✓] Yazıldı: {out_csv}  (satır: {len(df_fwd)})")
    print(df_fwd.head())
