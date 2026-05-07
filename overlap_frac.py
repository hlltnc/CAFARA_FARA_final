def overlap_frac(a1, b1, a2, b2, mode="new"):
    ov = max(0.0, min(b1, b2) - max(a1, a2))
    d1 = max(1e-12, b1 - a1)
    d2 = max(1e-12, b2 - a2)

    if mode == "new":
        return ov / d1
    if mode == "min":
        return ov / min(d1, d2)
    if mode == "union":
        return ov / (d1 + d2 - ov)
    raise ValueError("mode must be one of: new|min|union")
