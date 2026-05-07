import math

def calculate_successful_purification_rounds(rounds: int, purification_probability: float) -> int:
    """
    Planlanan purification turlarından beklenen başarılı tur sayısını döndürür.
    Rounds * purification_probability hesaplanır ve aşağı yuvarlanır.

    Args:
        rounds (int): Planlanan purification tur sayısı
        purification_probability (float): Her turun başarı olasılığı (0-1 arası)

    Returns:
        int: Beklenen başarılı purification tur sayısı (floor ile aşağı yuvarlanmış)
    """
    if rounds <= 0 or purification_probability <= 0:
        return 0
    expected_success = rounds * purification_probability
    successful_purification_rounds = math.floor(expected_success)
    return successful_purification_rounds
