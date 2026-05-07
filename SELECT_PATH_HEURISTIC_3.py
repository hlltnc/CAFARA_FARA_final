



from typing import List, Dict, Optional, Tuple, Any
import math, numbers

def select_best_and_backup_paths(
    path_infos: List[Dict[str, Any]],
    C_rel_th: float,
    overlap_mode: str = "edge",  # "edge" | "node" | "none"
    *,
    debug: bool = False,         # varsayılan: sessiz
    debug_limit: int = 10,
    return_stats: bool = False,  # True yaparsan stats üçüncü dönüş olarak gelir
    print_summary: bool = False, # kısa özet basmak istersen
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]] | Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Dict[str, Any]]:

    def _is_finite(x) -> bool:
        if isinstance(x, numbers.Number):
            return math.isfinite(float(x))
        if isinstance(x, str):
            try:
                return math.isfinite(float(x))
            except ValueError:
                return False
        return False

    def _to_float(x) -> Optional[float]:
        if _is_finite(x):
            return float(x)
        return None

    def _edges_undirected(path) -> set[frozenset]:
        if not isinstance(path, (list, tuple)) or len(path) < 2:
            return set()
        return {frozenset((u, v)) for u, v in zip(path[:-1], path[1:])}

    def _get_crel(p: Dict) -> Optional[float]:
        for k in ("C_rel_ent", "C_real", "C_rel_ent_resolved"):
            v = _to_float(p.get(k))
            if v is not None:
                return v
        return None

    def _get_egr(p: Dict) -> Optional[float]:
        v = _to_float(p.get("EGR_R_route"))
        if v is not None:
            return v
        E = p.get("EGR")
        if isinstance(E, dict):
            v2 = _to_float(E.get("R_route"))
            if v2 is not None:
                return v2
        return None

    stats: Dict[str, Any] = {
        "total_candidates": len(path_infos),
        "crel_threshold": float(C_rel_th),
        "overlap_mode": overlap_mode,
        # kapasite
        "cap_passed": 0,
        "cap_drop_uc_invalid": 0,
        "cap_drop_rbp_missing": 0,
        "cap_drop_uc_lt_rbp": 0,
        # crel
        "crel_passed": 0,
        "crel_drop_missing": 0,
        "crel_drop_below": 0,
        "max_crel_all": None,
        "max_crel_cap_pool": None,
        # egr
        "egr_missing_cnt": 0,
        # karar (istek bazında)
        "decision": None,      # "ok" | "drop_capacity" | "drop_crel" | "drop_egr"
        "drop_reason": None,
        # seçilenlerin metrikleri
        "best_egr": None, "best_crel": None,
        "backup_egr": None, "backup_crel": None,
    }

    # max_crel_all (bilgi)
    crels_all = []
    for p in path_infos:
        if isinstance(p, dict):
            c = _get_crel(p)
            if c is not None:
                crels_all.append(c)
    if crels_all:
        stats["max_crel_all"] = float(max(crels_all))

    # 1) Kapasite filtresi
    cap_ok_pool: List[Dict[str, Any]] = []
    for p in path_infos:
        if not isinstance(p, dict):
            continue
        uc  = _to_float(p.get("usable_capacity"))
        rbp = _to_float(p.get("required_bell_pairs"))

        if uc is None:
            stats["cap_drop_uc_invalid"] += 1
            continue

        rbp_val = rbp if rbp is not None else float("inf")
        if rbp is None:
            stats["cap_drop_rbp_missing"] += 1

        if uc >= rbp_val:
            cap_ok_pool.append(p)
        else:
            stats["cap_drop_uc_lt_rbp"] += 1

    stats["cap_passed"] = len(cap_ok_pool)
    if not cap_ok_pool:
        stats["decision"] = stats["drop_reason"] = "drop_capacity"
        if print_summary:
            print(f"[SUMMARY] drop_reason=capacity | total={stats['total_candidates']}")
        return (None, None, stats) if return_stats else (None, None)

    # 2) C_rel filtresi
    crel_ok_pool: List[Dict[str, Any]] = []
    crels_cap = []
    for p in cap_ok_pool:
        c = _get_crel(p)
        if c is None:
            stats["crel_drop_missing"] += 1
            continue
        crels_cap.append(c)
        if c >= C_rel_th:
            crel_ok_pool.append(p)
        else:
            stats["crel_drop_below"] += 1

    stats["crel_passed"] = len(crel_ok_pool)
    if crels_cap:
        stats["max_crel_cap_pool"] = float(max(crels_cap))

    if not crel_ok_pool:
        stats["decision"] = stats["drop_reason"] = "drop_crel"
        if print_summary:
            mx = stats['max_crel_cap_pool']
            print(f"[SUMMARY] drop_reason=C_rel | thr={C_rel_th:.3f} | max_crel_in_cap_pool={mx if mx is not None else 'None'}")
        return (None, None, stats) if return_stats else (None, None)

    # 3) EGR maksimum → best
    best_path = None
    best_egr = float("-inf")
    for p in crel_ok_pool:
        e = _get_egr(p)
        if e is None:
            stats["egr_missing_cnt"] += 1
            continue
        if e > best_egr:
            best_egr = e
            best_path = p

    if best_path is None:
        stats["decision"] = stats["drop_reason"] = "drop_egr"
        if print_summary:
            print(f"[SUMMARY] drop_reason=EGR_missing | crel_ok={len(crel_ok_pool)}")
        return (None, None, stats) if return_stats else (None, None)

    stats["best_egr"]  = _to_float(_get_egr(best_path))
    stats["best_crel"] = _to_float(_get_crel(best_path))

    # 4) Backup (overlap_mode)
    if overlap_mode == "edge":
        best_edges = _edges_undirected(best_path["path"])
        remaining_base = [
            p for p in crel_ok_pool
            if p is not best_path and _edges_undirected(p["path"]).isdisjoint(best_edges)
        ]
    elif overlap_mode == "node":
        best_nodes = set(best_path["path"])
        remaining_base = [
            p for p in crel_ok_pool
            if p is not best_path and set(p["path"]).isdisjoint(best_nodes)
        ]
    else:  # "none"
        remaining_base = [p for p in crel_ok_pool if p is not best_path]

    backup_path = None
    backup_egr = float("-inf")
    for p in remaining_base:
        e = _get_egr(p)
        if e is None:
            continue
        if e > backup_egr:
            backup_egr = e
            backup_path = p

    if backup_path is not None:
        stats["backup_egr"]  = _to_float(_get_egr(backup_path))
        stats["backup_crel"] = _to_float(_get_crel(backup_path))

    stats["decision"] = "ok"
    if print_summary:
        print(f"[SUMMARY] decision=ok | best_EGR={stats['best_egr']} | best_C_rel={stats['best_crel']} | backup={'yes' if backup_path else 'no'}")

    return (best_path, backup_path, stats) if return_stats else (best_path, backup_path)
