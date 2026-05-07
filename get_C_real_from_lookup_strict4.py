#get_C_real_from_lookup_strict4


import numpy as np
import pandas as pd
from typing import Optional, Tuple, Dict, Any

# ---------- helpers ----------

def _choose_C_col(df: pd.DataFrame, prefer=("C_real","C_rel","C","coherence")) -> str:
    for c in prefer:
        if c in df.columns:
            return c
    lower_map = {c.lower(): c for c in df.columns}
    for c in prefer:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    raise KeyError("lookup_df must contain one of: " + ", ".join(prefer))

def _pav_isotonic_increasing(y: np.ndarray) -> np.ndarray:
    """Basit PAV (isotonic) – artan monotonik en yakın yaklaşım."""
    y = np.asarray(y, dtype=float)
    blocks = [(y[i], 1) for i in range(len(y))]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i+1][0]:
            num = blocks[i][0]*blocks[i][1] + blocks[i+1][0]*blocks[i+1][1]
            den = blocks[i][1] + blocks[i+1][1]
            blocks[i:i+2] = [(num/den, den)]
            i = max(i-1, 0)
        else:
            i += 1
    return np.concatenate([np.full(w, v) for v, w in blocks])

def _interp_C_at_F_mono(
    df_one_L: pd.DataFrame,
    fe2e_req: float,
    C_col: str,
    *,
    out_of_range: str = "nan",   # {"clip","nan","extrapolate"}
    cmin: float = 0.0,
    cmax: float = 1.0,
    debug: bool = False
) -> Tuple[Optional[float], str, Optional[Dict[str, Any]]]:
    """
    Tek L dilimi için FE2E->C interpolasyonu.
    - C(F) isotonic (PAV) ile monotonikleştirilir.
    - out_of_range: veri aralığı dışındaki FE2E davranışı.
    - Sonuç [cmin, cmax] aralığına clip'lenir.
    - TEPE ÖNLEYİCİ: Interpolasyon sonucu dizideki en büyük C'ye eşitse,
      en büyük yerine ikinci en büyük değere sınırlandırılır (tam sabitse çok az aşağı çekilir).
    """
    status = []
    dbg = {} if debug else None

    sl = df_one_L.dropna(subset=["FE2E", C_col]).copy()
    if sl.empty:
        return None, "no_rows", dbg

    sl["FE2E"] = pd.to_numeric(sl["FE2E"], errors="coerce")
    sl[C_col]  = pd.to_numeric(sl[C_col],  errors="coerce")
    sl = sl.dropna(subset=["FE2E", C_col])
    if sl.empty:
        return None, "no_valid_rows", dbg

    g = sl.groupby("FE2E", as_index=False)[C_col].mean().sort_values("FE2E").reset_index(drop=True)
    fe = g["FE2E"].to_numpy(float)
    cr_raw = g[C_col].to_numpy(float)
    if debug:
        dbg.update(dict(fe_grid=fe.copy(), C_raw=cr_raw.copy()))

    if fe.size == 0:
        return None, "no_points", dbg
    if fe.size == 1:
        val = float(np.clip(cr_raw[0], cmin, cmax))
        return val, "single_point", dbg

    cr = _pav_isotonic_increasing(cr_raw)
    if debug:
        dbg["C_mono"] = cr.copy()

    F = float(fe2e_req)
    if F < fe[0]:
        if out_of_range == "clip":
            val = cr[0]; status.append("clipped_low")
        elif out_of_range == "nan":
            return None, "out_of_range_low", dbg
        else:
            slope = (cr[1] - cr[0]) / (fe[1] - fe[0])
            val = cr[0] + slope * (F - fe[0]); status.append("extrap_low")
    elif F > fe[-1]:
        if out_of_range == "clip":
            val = cr[-1]; status.append("clipped_high")
        elif out_of_range == "nan":
            return None, "out_of_range_high", dbg
        else:
            slope = (cr[-1] - cr[-2]) / (fe[-1] - fe[-2])
            val = cr[-1] + slope * (F - fe[-1]); status.append("extrap_high")
    else:
        val = float(np.interp(F, fe, cr))

    # --- TEPE ÖNLEYİCİ (anti-plateau cap) ---
    # cr'daki benzersiz değerleri toleranslı al; en büyük yerine ikinci en büyük değeri üst sınır yap.
    uniq = np.unique(np.round(cr, 12))
    if uniq.size >= 2:
        cap_hi = uniq[-2]                 # ikinci en büyük
    else:
        cap_hi = uniq[-1] - 1e-9          # tüm seri sabitse çok küçük aşağı çek

    max_val = uniq[-1]
    if val >= max_val - 1e-12:            # tepeye yapışıyorsa kes
        val = min(val, cap_hi)
        status.append("avoid_max")

    # Fiziksel aralığa sıkıştır
    val = float(np.clip(val, cmin, cmax))
    return val, (",".join(status) if status else "ok"), dbg

# ---------- main ----------

def get_C_real_at_required_FE2E(
    *,
    lookup_df: pd.DataFrame,
    M: int,
    X: int,
    L_km: float,
    FE2E_required: float,
    interpolate_L: bool = True,
    choose_L: str = "nearest",
    C_col_override: Optional[str] = "C_real",   # 5. sütun: C_real
    out_of_range: str = "nan",
    cmin: float = 0.0,
    cmax: float = 1.0,
    fe2e_policy: str = "clip_intersection",     # {"strict","clip_intersection","nearest_slice"}
    debug: bool = False
) -> Tuple[Optional[float], float, str, Optional[Dict[str, Any]]]:

    status_tags = []
    dbg = {} if debug else None

    # Sütun seçimi
    if C_col_override and (C_col_override in lookup_df.columns or C_col_override.lower() in {c.lower() for c in lookup_df.columns}):
        # case-insensitive düzeltme
        cmap = {c.lower(): c for c in lookup_df.columns}
        C_col = cmap.get(C_col_override.lower(), C_col_override)
        status_tags.append(f"col={C_col}")
    else:
        C_col = _choose_C_col(lookup_df, prefer=("C_real","C_rel","C","coherence"))
        if C_col_override:
            status_tags.append(f"col={C_col};override_missing({C_col_override})")
        else:
            status_tags.append(f"col={C_col}")

    # (M,X) filtresi
    M = int(M); X = int(X); L_km = float(L_km)
    sub = lookup_df[(lookup_df["M"].astype(int)==M) & (lookup_df["X"].astype(int)==X)].copy()
    if sub.empty:
        return None, np.nan, "no_rows_for_MX", dbg

    sub["L_km"]  = pd.to_numeric(sub["L_km"],  errors="coerce")
    sub["FE2E"]  = pd.to_numeric(sub["FE2E"],  errors="coerce")
    sub[C_col]   = pd.to_numeric(sub[C_col],   errors="coerce")
    sub = sub.dropna(subset=["L_km","FE2E",C_col])
    if sub.empty:
        return None, np.nan, "no_valid_rows_after_clean", dbg

    L_unique = np.sort(sub["L_km"].unique())
    if L_unique.size == 0:
        return None, np.nan, "no_L_values", dbg
    if debug:
        dbg["L_grid"] = L_unique.copy()

    def _range_for_L(Lfix: float) -> Tuple[float, float]:
        rows = sub[sub["L_km"] == Lfix][["FE2E", C_col]].dropna()
        return rows["FE2E"].min(), rows["FE2E"].max()

    def _interp_at_L(Lfix: float, F: float):
        rows_L = sub[sub["L_km"] == Lfix]
        return _interp_C_at_F_mono(
            rows_L, F, C_col,
            out_of_range=out_of_range, cmin=cmin, cmax=cmax, debug=debug
        )

    if interpolate_L and L_unique.size >= 2:
        j = np.searchsorted(L_unique, L_km)
        if j == 0:
            L0 = L1 = L_unique[0]; status_tags.append("clamped_low")
        elif j >= L_unique.size:
            L0 = L1 = L_unique[-1]; status_tags.append("clamped_high")
        else:
            L0 = L_unique[j-1]; L1 = L_unique[j]

        mn0, mx0 = _range_for_L(L0)
        mn1, mx1 = _range_for_L(L1)
        if debug:
            dbg.update(dict(L0=L0, L1=L1, FE2E_range_L0=(mn0,mx0), FE2E_range_L1=(mn1,mx1)))

        Freq = float(FE2E_required)
        if fe2e_policy == "clip_intersection":
            lo, hi = max(mn0, mn1), min(mx0, mx1)
            if lo <= hi:
                if Freq < lo or Freq > hi:
                    status_tags.append(f"fe2e_clipped_to_intersection[{lo:.4f},{hi:.4f}]")
                F_adj = min(max(Freq, lo), hi)
                C0, s0, d0 = _interp_at_L(L0, F_adj)
                C1, s1, d1 = _interp_at_L(L1, F_adj)
            else:
                status_tags.append("no_intersection")
                C0 = C1 = None; s0 = s1 = "no_intersection"
        elif fe2e_policy == "nearest_slice":
            in0 = (mn0 <= Freq <= mx0)
            in1 = (mn1 <= Freq <= mx1)
            if in0 and in1:
                C0, s0, d0 = _interp_at_L(L0, Freq)
                C1, s1, d1 = _interp_at_L(L1, Freq)
            elif in0:
                C0, s0, d0 = _interp_at_L(L0, Freq); C1, s1, d1 = None, "skipped_L1", None
                status_tags.append("used_L0_only")
            elif in1:
                C1, s1, d1 = _interp_at_L(L1, Freq); C0, s0, d0 = None, "skipped_L0", None
                status_tags.append("used_L1_only")
            else:
                # iki dilimde de dışarıda → en yakın uca kırp
                d0_abs = min(abs(Freq-mn0), abs(Freq-mx0))
                d1_abs = min(abs(Freq-mn1), abs(Freq-mx1))
                if d0_abs <= d1_abs:
                    F_adj = min(max(Freq, mn0), mx0)
                    status_tags.append("nearest=L0_clipped")
                    C0, s0, d0 = _interp_at_L(L0, F_adj); C1, s1, d1 = None, "skipped_L1", None
                else:
                    F_adj = min(max(Freq, mn1), mx1)
                    status_tags.append("nearest=L1_clipped")
                    C1, s1, d1 = _interp_at_L(L1, F_adj); C0, s0, d0 = None, "skipped_L0", None
        else:  # "strict"
            C0, s0, d0 = _interp_at_L(L0, Freq)
            C1, s1, d1 = _interp_at_L(L1, Freq)

        if debug:
            dbg.update(dict(L0_dbg=d0, L1_dbg=d1))

        if C0 is None and C1 is None:
            return None, float(L0), "no_data_on_bracket_L" if fe2e_policy=="strict" else ",".join(status_tags), dbg
        if C0 is None:
            return float(C1), float(L1), ",".join(["used_high_only"]+status_tags), dbg
        if C1 is None:
            return float(C0), float(L0), ",".join(["used_low_only"]+status_tags), dbg

        w = 0.0 if L1==L0 else (L_km - L0)/(L1 - L0)
        C_out = (1.0 - w)*C0 + w*C1
        return float(C_out), float(L_km), ("ok" if not status_tags else ",".join(status_tags)), dbg

    # tek dilim
    if choose_L == "nearest":
        idx = np.abs(L_unique - L_km).argmin()
    elif choose_L == "low":
        idx = max(0, np.searchsorted(L_unique, L_km) - 1)
    elif choose_L == "high":
        idx = min(L_unique.size - 1, np.searchsorted(L_unique, L_km))
    else:
        raise ValueError("choose_L must be one of {'nearest','low','high'}")

    L_sel = float(L_unique[idx])
    if debug:
        dbg["L_sel"] = L_sel

    C_out, s, d = _interp_at_L(L_sel, float(FE2E_required))
    if debug:
        dbg["L_sel_dbg"] = d
    if s != "ok": status_tags.append(s)
    if C_out is None:
        return None, L_sel, "no_data_on_selected_L", dbg
    return float(C_out), L_sel, ("ok" if not status_tags else ",".join(status_tags)), dbg
