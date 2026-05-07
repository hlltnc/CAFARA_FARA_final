def check_and_select_valid_path(G, best_path, backup_path, min_fidelity):
    """
    Best path’in G üzerinde geçerli olup olmadığını kontrol eder.
    Eğer herhangi bir edge fidelity = 0.5 ise backup path’e geçer.

    Returns:
        valid_path: kullanılacak path (best veya backup)
        used_backup: True/False
    
    
    
    
    """

    def path_has_failure(path, G, min_fid):
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            fid = G[u][v].get("fidelity", 1.0)
            if fid <= min_fid:
                return True
        return False

    if not best_path:
        return None, False

    if not path_has_failure(best_path["path"], G, min_fidelity):
        return best_path, False  # Best path kullanılabilir

    elif backup_path and not path_has_failure(backup_path["path"], G, min_fidelity):
        return backup_path, True  # Best bozuk ama backup kullanılabilir

    else:
        return None, False  # İkisi de uygun değil