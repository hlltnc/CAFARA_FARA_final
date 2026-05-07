

import random
import math
import pandas as pd



def calculate_time_windows(df):
    all_results = []

    for idx, row in df.iterrows():
        arrival_time = row['arrival_time']
        leave_time = row['leave_time']
        request_time_window = math.ceil(abs(leave_time - arrival_time))
        primary_placement_window = math.ceil(request_time_window / 2)
        backup_placement_window = request_time_window - primary_placement_window

        primary_probs = []
        backup_probs = []

        for i in range(1, request_time_window + 1):
            if i <= primary_placement_window:
                primary_probs.append(round(i / primary_placement_window, 3))
                backup_probs.append(0.0)
            else:
                primary_probs.append(1.0)
                backup_index = i - primary_placement_window
                backup_probs.append(round(backup_index / backup_placement_window, 3))

        all_results.append({
            "Request ID": idx,
            "Request_Time_Window": request_time_window,
            "Primary_placement_window": primary_placement_window,
            "Backup_placement_window": backup_placement_window,
            "Primary_probs": primary_probs,
            "Backup_probs": backup_probs
        })

    return pd.DataFrame(all_results)
