def calculate_required_threshold(f_threshold, path):
    """
    Verilen path'e göre, her bir edge'in minimum sağlaması gereken fidelity threshold'u hesaplar.
    
    Args:
        f_threshold (float): Request'ten gelen genel fidelity threshold.
        path (list): Source → Destination yolunu gösteren node listesidir.

    Returns:
        float: Her bir edge için gerekli minimum fidelity threshold.
    """
    num_edges = len(path) - 1  # path üzerindeki edge sayısı

    if num_edges == 0:
        return 1.0  # path sadece bir node ise threshold etkilenmez

    required_f_threshold = f_threshold ** (1 / num_edges)
    return required_f_threshold