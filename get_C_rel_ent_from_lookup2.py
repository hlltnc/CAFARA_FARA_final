import pandas as pd
import numpy as np

def get_C_rel_ent_from_lookup(M, X, L, FE2E_target, lookup_df, fe2e_tol, l_tol):
    """
    Verilen M, X, L ve hedef FE2E değeri için en yakın C_rel_ent değerini döner.
    Hiçbir zaman None döndürmez; en yakın sonucu verir.

    Dönüş:
        (C_rel_ent, FE2E, status)
    """
    # M ve X filtre
    subset = lookup_df[(lookup_df['M'] == M) & (lookup_df['X'] == X)].copy()
    if subset.empty:
        # M, X yoksa tüm tabloda en yakın değeri ara
        nearest = lookup_df.iloc[((lookup_df["L_km"] - L)**2).argsort().iloc[0]]
        return float(nearest["C_rel_ent"]), float(nearest["FE2E"]), "nearest_all"

    # L toleransı
    subset_L = subset[subset['L_km'].between(L - l_tol, L + l_tol)].copy()
    if subset_L.empty:
        # En yakın L'yi seç (M, X sabit)
        nearest = subset.iloc[(subset["L_km"] - L).abs().argsort().iloc[0]]
        return float(nearest["C_rel_ent"]), float(nearest["FE2E"]), "nearest_L"

    # FE2E farkı
    subset_L["fe2e_diff"] = (subset_L["FE2E"] - FE2E_target).abs()

    # Tolerans içindeyse
    within_tol = subset_L[subset_L["fe2e_diff"] <= fe2e_tol].copy()
    if within_tol.empty:
        # Tolerans içinde yoksa en yakın FE2E
        best = subset_L.sort_values("fe2e_diff").iloc[0]
        return float(best["C_rel_ent"]), float(best["FE2E"]), "nearest_FE2E"

    # En yakın eşleşme (tam tolerans içinde)
    best = within_tol.sort_values("fe2e_diff").iloc[0]
    return float(best["C_rel_ent"]), float(best["FE2E"]), "exact"
