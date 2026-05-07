def sort_requests(df_requests):
    return df_requests.sort_values(by=['arrival_time', 'leave_time']).reset_index(drop=True)
