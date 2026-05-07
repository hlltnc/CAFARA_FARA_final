


from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpBinary, PULP_CBC_CMD

def select_best_path_ILP(path_infos):
    """
    ILP ile usable_capacity ≥ required_bell_pairs koşulunu sağlayan path'ler arasından
    C_rel.ent (relative entropy of coherence) değerini maksimize eden path'i seçer.
    """
    # 1. Filtrele: sadece constraint uyumlu path'ler
    filtered_paths = []
    for i, p in enumerate(path_infos):
        if (
            p.get("usable_capacity") is not None and
            p.get("required_bell_pairs") is not None and
            p.get("C_rel_ent") is not None and
            p["required_bell_pairs"] <= p["usable_capacity"]
        ):
            filtered_paths.append((i, p))

    if not filtered_paths:
        print("No valid path satisfies the constraint.")
        return None

    # 2. ILP modeli oluştur
    model = LpProblem("Select_Best_Path", LpMaximize)

    # 3. Binary değişkenler tanımla (her path için bir x_i)
    x_vars = {
        i: LpVariable(f"x_{i}", cat=LpBinary)
        for i, _ in filtered_paths
    }

    # 4. Amaç fonksiyonu: C_rel_ent değerlerini maksimize et
    model += lpSum(
        x_vars[i] * p["C_rel_ent"] for i, p in filtered_paths
    )

    # 5. Constraint: yalnızca bir path seçilsin
    model += lpSum(x_vars[i] for i, _ in filtered_paths) == 1

    # 6. ILP çöz (sessiz modda)
    model.solve(PULP_CBC_CMD(msg=0))

    # 7. En iyi path’i döndür
    for i, p in filtered_paths:
        if x_vars[i].value() == 1:
            return p

    return None  # çözüm bulunamazsa