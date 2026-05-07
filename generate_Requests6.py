

import random
import pandas as pd

def generate_requests(num_requests, num_nodes, demand_range, f_threshold_range, windows_time, lifetime_ratio_range):
    requests = []

    for i in range(num_requests):
        source = random.randint(0, num_nodes - 1)
        destination = random.randint(0, num_nodes - 1)
        while destination == source:
            destination = random.randint(0, num_nodes - 1)

        # Arrival time: tüm request'ler windows_time aralığında gelecek
        arrival_time = round(random.uniform(0, windows_time), 2)

        # Lifetime: her request için farklı bir oranla belirleniyor
        lifetime_ratio = random.uniform(lifetime_ratio_range[0], lifetime_ratio_range[1])
        lifetime = round(lifetime_ratio * windows_time, 2)
        leave_time = round(arrival_time + lifetime, 2)

        demand = random.randint(demand_range[0], demand_range[1])
        f_threshold = round(random.uniform(f_threshold_range[0], f_threshold_range[1]), 3)

        request = {
            'Request ID': i,
            'Request_Time_Window': lifetime,
            'arrival_time': arrival_time,
            'leave_time': leave_time,
            'source': source,
            'destination': destination,
            'demand': demand,
            'f_threshold': f_threshold
        }

        requests.append(request)

    return pd.DataFrame(requests)
