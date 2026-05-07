# calculate_required_threshold_C_rel


import numpy as np
import pandas as pd
from typing import Sequence, Dict, Any, Optional, Tuple

# --- C sütununu akıllı çöz (case-insensitive + eşanlamlılar) ---
def _resolve_C_column(df: pd.DataFrame) -> Optional[str]:
    cand = ["C_rel", "C_real", "Crel", "C_rel_entropy", "C_rel_coherence", "C"]
    cols = {c.lower(): c for c in df.columns}
    for c in cand:
        if c.lower() in cols:
            return cols[c.lower()]
    return None

def _prep_slice(df_one_L: pd.DataFrame, C_col_name: str) -> pd.DataFrame:
    sl = df_one_L.dropna(subset=["FE2E", C_col_name]).copy()
    if sl.empty:
        return sl
    sl[C_col_name] = pd.to_numeric(sl[C_col_name], errors="coerce")
    sl["FE2E"]      = pd.to_numeric(sl["FE2E"],      errors="coerce")
    sl = sl.dropna(subset=[C_col_name, "FE2E"])
    # Her C için min FE2E’yi al, C’ye göre sırala ve FE2E’yi monotonikleştir
    g = (sl.groupby(C_col_name, as_index=False)["FE2E"].min()
           .sort_values(C_col_name).reset_index(drop=True))
    g["FE2E_mono"] = g["FE2E"].cummax()
    g = g.rename(columns={C_col_name: "C_rel"})
    return g

def _interp_min_FE2E_for_C(df_one_L: pd.DataFrame, C_rel_th: float
) -> Optional[Tuple[float, float]]:
    """
    Tek (M,X,L) diliminde, C>=hedef için gereken min FE2E’yi döndürür.
    ÇIKTI: (FE2E_required, C_rel_matched)
    """
    C_col = _resolve_C_column(df_one_L)
    if C_col is None:
        return None
    g = _prep_slice(df_one_L, C_col)
    if g.empty:
        return None

    cr = g["C_rel"].to_numpy(float)
    fe = g["FE2E_mono"].to_numpy(float)
    C_th = float(C_rel_th)

    # Hedefi veri aralığına sıkıştır: raporlamak için gerekli
    C_eff = float(np.clip(C_th, cr.min(), cr.max()))
    F_req = float(np.interp(C_th, cr, fe, left=fe[0], right=fe[-1]))
    return F_req, C_eff

def _nearest_FE2E_for_C(
    df_one_L: pd.DataFrame, C_rel_th: float, *, prefer_below: bool = False
) -> Optional[Tuple[float, float]]:
    """
    En yakın C noktasındaki (C_match, FE2E_mono) döner.
    """
    C_col = _resolve_C_column(df_one_L)
    if C_col is None:
        return None
    g = _prep_slice(df_one_L, C_col)
    if g.empty:
        return None

    cr = g["C_rel"].to_numpy(float)
    fe = g["FE2E_mono"].to_numpy(float)
    th = float(C_rel_th)

    if prefer_below:
        below = np.where(cr <= th)[0]
        if below.size:
            i = below[np.argmin(np.abs(cr[below] - th))]
            return float(cr[i]), float(fe[i])
        above = np.where(cr > th)[0]
        if above.size:
            i = above[np.argmin(np.abs(cr[above] - th))]
            return float(cr[i]), float(fe[i])
        return None
    else:
        i = int(np.abs(cr - th).argmin())
        return float(cr[i]), float(fe[i])

# --- SABİT C kontrolü ---
def _const_C_info(df_one_L: pd.DataFrame) -> Tuple[bool, float, Tuple[float, float]]:
    """
    Dilimde C sabitse True döner ve (C_const, (FE2E_min, FE2E_max)) verir.
    Aksi halde (False, np.nan, (np.nan, np.nan)).
    """
    C_col = _resolve_C_column(df_one_L)
    if C_col is None or df_one_L.empty:
        return False, np.nan, (np.nan, np.nan)
    C_vals = pd.to_numeric(df_one_L[C_col], errors="coerce").dropna().unique()
    if C_vals.size == 1:
        constC = float(C_vals[0])
        fe = pd.to_numeric(df_one_L["FE2E"], errors="coerce").dropna()
        return True, constC, (float(fe.min()) if not fe.empty else np.nan,
                              float(fe.max()) if not fe.empty else np.nan)
    return False, np.nan, (np.nan, np.nan)

def select_required_F_and_M(
    path: Sequence[int],
    *,
    lookup_df: pd.DataFrame,      # zorunlu sütunlar: ["M","X","L_km","FE2E", <C sütunu>]
    C_rel_design: float,          # hedef koherens
    L_per_hop_km: float,          # her hop uzunluğu (km)
    selection_policy: str = "min_satisfy",  # "min_satisfy" | "max"
    F_threshold: Optional[float] = None,
    prefer_below_on_nearest: bool = False
) -> Dict[str, Any]:
    """
    Aynı akış; ek olarak C_rel_matched döndürülür.
    Sabit C dilimlerinde 'reason' içine 'const_C_slice' eklenir.
    """
    C_col = _resolve_C_column(lookup_df)
    if C_col is None:
        raise KeyError("lookup_df must contain a C coherence column (e.g. 'C_rel').")
    need = {"M", "X", "L_km", "FE2E", C_col}
    if not need.issubset(lookup_df.columns):
        missing = sorted(list(need - set(lookup_df.columns)))
        raise KeyError(f"lookup_df missing columns: {missing}")

    X = max(0, len(path) - 1)
    if X == 0:
        return dict(F_target=1.0, M_selected=0, X=0, L_matched_km=0.0,
                    C_rel_design=float(C_rel_design), C_rel_matched=1.0, reason="trivial_path")

    subX = lookup_df[lookup_df["X"].astype(int) == int(X)].copy()
    if subX.empty:
        return dict(F_target=np.nan, M_selected=np.nan, X=X,
                    L_matched_km=np.nan, C_rel_design=float(C_rel_design),
                    C_rel_matched=np.nan, reason="no_rows_for_X")

    L_req = float(L_per_hop_km)
    idx = (pd.to_numeric(subX["L_km"], errors="coerce") - L_req).abs().idxmin()
    L_matched = float(subX.loc[idx, "L_km"])
    subXL = subX[subX["L_km"] == L_matched].copy()
    if subXL.empty:
        return dict(F_target=np.nan, M_selected=np.nan, X=X,
                    L_matched_km=L_matched, C_rel_design=float(C_rel_design),
                    C_rel_matched=np.nan, reason="no_rows_for_XL")

    M_vals = np.sort(subXL["M"].dropna().astype(int).unique())
    if M_vals.size == 0:
        return dict(F_target=np.nan, M_selected=np.nan, X=X,
                    L_matched_km=L_matched, C_rel_design=float(C_rel_design),
                    C_rel_matched=np.nan, reason="no_M_values")

    C_used = np.nan
    reason = ""

    if selection_policy == "max":
        M_selected = int(M_vals.max())
        df_one = subXL[subXL["M"].astype(int) == M_selected]
        # Sabit C mi?
        is_const, c_const, (fe_min, _) = _const_C_info(df_one)
        if is_const:
            C_used = c_const
            F_target = fe_min if np.isfinite(fe_min) else np.nan
            reason = "const_C_slice"
        else:
            out = _interp_min_FE2E_for_C(df_one, float(C_rel_design))
            if out is None:
                near = _nearest_FE2E_for_C(df_one, float(C_rel_design),
                                           prefer_below=prefer_below_on_nearest)
                if near is not None:
                    C_match, F_match = near
                    F_target = F_match
                    C_used = C_match
                    reason = f"nearest_match(M={M_selected}, C_match={C_match:.6f})"
                else:
                    fevals = pd.to_numeric(df_one["FE2E"], errors="coerce").dropna().values
                    F_target = float(fevals.max()) if fevals.size else np.nan
                    reason = "unsatisfied_take_maxFE2E"
            else:
                F_target, C_used = out
                reason = "ok_max"

    elif selection_policy == "min_satisfy":
        M_selected = None
        F_target = None
        for m in M_vals:
            df_one = subXL[subXL["M"].astype(int) == int(m)]
            # Sabit C kontrolü
            is_const, c_const, (fe_min, _) = _const_C_info(df_one)
            c_max = pd.to_numeric(df_one[_resolve_C_column(df_one)], errors="coerce").max()
            if np.isnan(c_max) or c_max < float(C_rel_design):
                continue
            if is_const:
                M_selected = int(m)
                C_used = c_const
                F_target = fe_min if np.isfinite(fe_min) else np.nan
                reason = "ok_min_satisfy|const_C_slice"
                break
            out = _interp_min_FE2E_for_C(df_one, float(C_rel_design))
            if out is not None:
                F_target, C_used = out
                M_selected = int(m)
                reason = "ok_min_satisfy"
                break
        if M_selected is None:
            best = None  # (delta, M, C_match, F_match)
            for m in M_vals:
                df_one = subXL[subXL["M"].astype(int) == int(m)]
                near = _nearest_FE2E_for_C(df_one, float(C_rel_design),
                                           prefer_below=prefer_below_on_nearest)
                if near is None:
                    continue
                C_match, F_match = near
                delta = abs(C_match - float(C_rel_design))
                tpl = (delta, int(m), C_match, F_match)
                if (best is None) or (tpl < best):
                    best = tpl
            if best is not None:
                _, M_selected, C_used, F_target = best
                reason = f"nearest_match(M={M_selected}, C_match={C_used:.6f})"
            else:
                m = int(M_vals.max())
                df_one = subXL[subXL["M"].astype(int) == m]
                fevals = pd.to_numeric(df_one["FE2E"], errors="coerce").dropna().values
                F_target = float(fevals.max()) if fevals.size else np.nan
                M_selected = m
                reason = "unsatisfied_take_maxFE2E"
    else:
        raise ValueError("selection_policy must be 'min_satisfy' or 'max'")

    # --- KORUMA: F_min_per_link tabanı (opsiyonel) ---
    if F_threshold is not None and np.isfinite(F_threshold) and X > 0:
        F_th = float(np.clip(F_threshold, 0.0, 1.0))
        F_min_per_link = F_th ** (1.0 / float(X))
        if F_target is None or not np.isfinite(F_target) or F_target < F_min_per_link:
            F_target = F_min_per_link
            reason = (reason + "|raised_to_Fmin_per_link") if isinstance(reason, str) else "raised_to_Fmin_per_link"

    if F_target is not None and np.isfinite(F_target):
        F_target = float(np.clip(F_target, 0.0, 1.0))

    return dict(
        F_target=F_target,
        M_selected=int(M_selected) if M_selected is not None else np.nan,
        X=int(X),
        L_matched_km=L_matched,
        C_rel_design=float(C_rel_design),
        C_rel_matched=float(C_used) if np.isfinite(C_used) else np.nan,
        reason=reason
    )
