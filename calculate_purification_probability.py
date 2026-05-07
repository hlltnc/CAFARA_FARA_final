def purification_probability(F_initial, F2=None):
    """
    Calculate the purification success probability for given fidelities.
    
    Args:
        F_initial (float): Fidelity of the first Bell pair (0 < F < 1)
        F2 (float, optional): Fidelity of the second Bell pair (0 < F < 1).
                              If None, F2 is assumed to be equal to F_initial.
    
    Returns:
        float: Purification success probability P_succ
    """
    if not (0 < F_initial < 1):
        raise ValueError("F_initial must be between 0 and 1 (exclusive).")

    
    P_succ = F_initial **2 + (1 - F_initial)**2
    return P_succ