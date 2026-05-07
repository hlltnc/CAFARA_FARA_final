import numpy as np
import pandas as pd

def get_C_real_from_lookup(
    M: int,
    X: int,
    L: float = None,
    FE2E_target: float = None,   # kullanılmıyor; imza uyumu için
    lookup_df: pd.DataFrame = None,
    *,
    l_tol: float ,          # L grid adımın 1 km ise 0.5 iyi
    interpolate: bool = True,
    **kwargs
):
    """
    FE2E_forward_lookup.csv içinden C_real(L) döndürür.
    Dönen: (C_real, matched_FE2E, status)
      status ∈ {'ok','no_lookup','no_match_MX','no_match_L'}

    Notlar:
    - L birimi: km (tablodaki L_km ile aynı olmalı)
    - interpolate=True: L etrafında lineer interpolasyon dener, yoksa en yakın komşu.
    - FE2E_target parametresi sadece imzayı korumak için var; kullanılmaz.
    """
    if lookup_df is None or not isinstance(lookup_df, pd.DataFrame):
        return (None, None, "no_lookup")

    # L parametresini L veya L_x adıyla almayı destekle
    if L is None and "L_x" in kwargs:
        L = kwargs["L_x"]
    if L is None:
        return (None, None, "no_match_L")

    # M & X filtresi
    sub = lookup_df[(lookup_df["M"] == int(M)) & (lookup_df["X"] == int(X))]
    if sub.empty:
        return (None, None, "no_match_MX")

    # L'e en yakın satırı bul
    L_vals = sub["L_km"].values.astype(float)
    diffs = np.abs(L_vals - float(L))
    i = diffs.argmin()
    min_diff = float(diffs[i])

    # Tolerans kontrolü (tablo aralığının çok dışındaysa)
    if min_diff > float(l_tol):
        return (None, None, "no_match_L")

    # İsteğe bağlı lineer interpolasyon (L ekseninde)
    if interpolate and len(sub) >= 2:
        # İki yandaki noktaları bul
        # Sıralı index
        order = np.argsort(L_vals)
        L_sorted = L_vals[order]
        C_sorted = sub["C_real"].values.astype(float)[order]
        F_sorted = sub["FE2E"].values.astype(float)[order]

        # Aralık içinde mi?
        if L_sorted[0] <= L <= L_sorted[-1]:
            # Sağ komşuyu bul
            j = np.searchsorted(L_sorted, L)
            if j == 0:
                C_val = C_sorted[0]
                F_val = F_sorted[0]
            elif j >= len(L_sorted):
                C_val = C_sorted[-1]
                F_val = F_sorted[-1]
            else:
                # lineer interpolasyon
                L0, L1 = L_sorted[j-1], L_sorted[j]
                t = 0.0 if L1 == L0 else (L - L0) / (L1 - L0)
                C_val = C_sorted[j-1] + t * (C_sorted[j] - C_sorted[j-1])
                F_val = F_sorted[j-1] + t * (F_sorted[j] - F_sorted[j-1])
            return (float(C_val), float(F_val), "ok")

    # Aksi halde en yakın komşu
    row = sub.iloc[i]
    C_real = float(row["C_real"])
    FE2E = float(row["FE2E"]) if "FE2E" in row else None
    return (C_real, FE2E, "ok")
