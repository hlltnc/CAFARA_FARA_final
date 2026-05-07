


def sort_requests_by_backup_window(windows_df):
    sorted_requests = windows_df.sort_values(by='Backup_placement_window', ascending=True).reset_index(drop=True)
    return sorted_requests
