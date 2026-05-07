def final_fidelity_after_purification(F_initial, successful_rounds):
    if not (0 < F_initial < 1):
        raise ValueError("F_initial must be in (0,1).")
    if successful_rounds < 0:
        raise ValueError("successful_rounds must be >= 0.")
    F_current = F_initial
    for _ in range(int(successful_rounds)):  # güvenli cast
        num = F_current**2
        den = num + (1 - F_current)**2
        F_current = num / den
    return F_current

