def sort_paths_by_intermediate_nodes(paths):
    """
    Path listesini intermediate node sayısına göre sıralar (artan sırada).
    
    Input:
        paths: Liste [ [node1, node2, ..., nodeN], ... ]
    
    Output:
        sorted_paths: Intermediate node sayısına göre sıralanmış path listesi
    """
    return sorted(paths, key=lambda path: len(path) - 2)
