#fideliteye gore purification


from  generate_WAXMAN_network5 import create_network
from assign_fidelities_to_the_edges import assign_fidelity_to_edges
from calculate_purification_rounds2 import calculate_purification_rounds
from assign_EDP import assign_entanglement_distribution_probabilities
from assing_ESP_to_nodes import assign_swapping_probabilities
import networkx as nx
from Calculate_ESP_for_PATH import calculate_esp_for_path
from generate_Requests6 import generate_requests
from assign_filtered_capacities import assign_filtered_capacities
from sort_requests import sort_requests
from get_all_edge_disjoint_paths import get_all_edge_disjoint_paths
from sort_paths_by_intermediate_nodes import sort_paths_by_intermediate_nodes
from assign_capacity_from_values import assign_capacity_from_values
from calculate_usable_capacity_for_path import calculate_usable_capacity_for_path
from calculate_required_threshold_C_rel import select_required_F_and_M
import random
from compute_required_bell_pairs2 import compute_required_bell_pairs
from calculate_windows import calculate_time_windows
from sort_requests_by_backup_window import sort_requests_by_backup_window
#from calculate_relative_entropy_of_coherence3 import estimate_C_rel_ent
from assign_fixed_distance import assign_fixed_distance
from select_best_path_ILP import select_best_path_ILP
#from select_best_and_backup_path_ILP import select_best_and_backup_path_ILP
from SELECT_PATH_HEURISTIC_3 import select_best_and_backup_paths
from add_link_failures_by_percentage import add_link_failures_by_percentage
from check_and_select_valid_path import check_and_select_valid_path
from calculate_success_rate import calculate_success_rate
from calculate_entanglement_generation_time import calculate_entanglement_generation_time
from calculate_total_entanglement_time import calculate_total_entanglement_time
from calculate_swapping_time import calculate_swapping_time
from calculate_stats import calculate_stats
#from calculate_purification_time_full import calculate_purification_time_full
from calculate_total_purification_time_from_path import calculate_total_purification_time_from_path
from get_C_rel_ent_from_lookup2 import get_C_rel_ent_from_lookup
import Entanglement_generation_rate as egr
from get_C_real_from_lookup import get_C_real_from_lookup
from path_length_km_from_graph import _is_num
from path_length_km_from_graph import path_length_km_from_graph
from get_C_real_from_lookup_strict4 import get_C_real_at_required_FE2E
from calculate_required_threshold import calculate_required_threshold
from calculate_successful_purification_rounds import calculate_successful_purification_rounds
from calculate_purification_probability import purification_probability
from final_fidelity_after_purification import final_fidelity_after_purification
from compute_path_final_fidelity import compute_path_final_fidelity
from overlap_frac import overlap_frac


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


lookup_df_real = pd.read_csv("FE2E_forward_lookup.csv")


repetition = 10


All_req_rounds=[]
All_req_latency=[]
All_req_t_ent=[]
All_req_t_purif=[]
All_req_t_swap=[]
All_req_path_hops=[]
All_req_path_len_km=[]




# Store results
all_avg_success_rates = []
all_avg_fidelities = []
all_avg_coherence_values = []
all_avg_S_coherence_values =[]
all_avg_Latency =[]
all_avg_rounds=[]
all_avg_rounds_needed=[]



all_avg_drop_capacity = []
all_avg_drop_crel = []
all_avg_drop_egr = []
all_avg_drop_time = []
all_avg_drop_link_fail = []
all_avg_drop_total = []
all_avg_drop_fid =[]
fixed_distance=1


step = 5

NUM_REQ_list = np.arange(10, 250+step , step )


for NUM_REQ in NUM_REQ_list:
   

    #print(f"\n Fixed Distance = {fixed_distance} km")
    success_rates = []
    Latency_dizin =[]
    success_coherences_all = [] 

    final_fidelities = [] 
    coherence_values = []
    rounds_dizin= []
    rounds_needed_dizin = []


    success_rates = []
    drop_rates = []  # total
    drop_rates_capacity = []
    drop_rates_crel = []
    drop_rates_egr = []
    drop_rates_time = []
    drop_rates_link_fail = []
    drop_rates_fid=[]



    all_req_rounds = []
    all_req_latency = []
    all_req_t_ent = []
    all_req_t_purif = []
    all_req_t_swap = []
    all_req_path_hops = []
    all_req_path_len_km = []
    all_req_freq = []
    



    for rep in range(repetition):
        print(f"   🔁 Repetition {rep + 1}/{repetition}")
        accepted_reservations = []  # [(arr, lev, set_of_edges)]
        drop_count_overlap = 0    

        #fixed_distance=100  #km 
        Crel_th=0.7
        #Crel_design=Crel_th
        ESP_probability_range=(0.7,0.95)
        EDP_Probability_range=(0.65, 0.95)
        Num_of_nodes=10
        Initial_Fidelity_range=(0.70, 0.99)
        #NUM_REQ=50
        windows_time = 5
        DEMAND_RANGE=(10, 10)
        F_THRESHOLD_RANGE=(0.80, 0.80)
        freq_for_capacity=100
        CAPACITY_RANGE=(0,1000)
        elemantary_entanglement_generation_rate=0.8
        F_initial = random.uniform(0.70, 0.99)
        lifetime_ratio_range=(0.1, 0.9)
        overlap_th=0.99


#F_threshold = 0.7  # örnek bir eşik değeri
        L_att=fixed_distance*1000
        kappa = 0.2
        alpha = 0.02
        L=fixed_distance




        df_requests = generate_requests(
            num_requests=NUM_REQ,
            num_nodes=Num_of_nodes,
            demand_range=DEMAND_RANGE,
            f_threshold_range=F_THRESHOLD_RANGE,
            windows_time=windows_time,
            lifetime_ratio_range=lifetime_ratio_range
            )

        df_sorted = sort_requests(df_requests)





        all_path_info_per_request = []
        G_per_request = []  # tüm G'leri sırayla kaydederiz

        for idx, request in df_sorted.iterrows():
            print(f"\n🔷 Request {idx}: {request['source']} → {request['destination']}")


    # 1. Ağ yeniden oluşturuluyor
            G = create_network(
              n=Num_of_nodes,
              alpha=0.45, beta=0.20,
              target_avg_degree=3.0,      # daha fazla hop/swap için 2.5–3.5 iyi
              ensure_connected=True,
              scale_km_per_unit=fixed_distance,
              seed=42,
              add_distance_fields=True,
              add_fidelity=True,
              fidelity_range=Initial_Fidelity_range
            )
            
            G = assign_entanglement_distribution_probabilities(G, prob_range=EDP_Probability_range)
            G = assign_swapping_probabilities(G, prob_range=ESP_probability_range)
            
            G = nx.convert_node_labels_to_integers(G)


    


    # 2. Kapasiteyi atama
            G = assign_filtered_capacities(
                G,
                freq_for_capacity=freq_for_capacity,
                CAPACITY_RANGE=CAPACITY_RANGE,
                elementary_entanglement_generation_rate=elemantary_entanglement_generation_rate
            )

# LİSTE -> SKALER dönüşümü (len). İstersen 0’ları önlemek için max(1, ...)
            edge_values = {
             (u, v): max(1, len(G[u][v].get('capacities', [])))   # 0'ları taban 1 yapıyoruz
             for u, v in G.edges()
            }

# Skaler kapasiteyi 'capacity' alanına yaz (listeyi ezmeyelim)
            G = assign_capacity_from_values(G, edge_values, field_name='capacity')
    # 3. Path ve hesaplamalar
            source = int(request['source'])
            destination = int(request['destination'])
            f_threshold = request['f_threshold']
            demand = request['demand']
    
            G_per_request.append(G)


            paths = get_all_edge_disjoint_paths(G, request)


            if not paths:
                print("  → No path found.")
                all_path_info_per_request.append([])
                continue

    
   
            path_infos = []

            for path in paths:
                path = [int(n) for n in path]
                intermediate_nodes = path[1:-1]
      
               

                required_thresh = calculate_required_threshold(f_threshold, path)

                print(f"FE2E_required = {required_thresh:.4f}")


                F_initial_2 = 0.5 + (F_initial - 0.5) * np.exp(-alpha * L)

                rounds , F_final_1 = calculate_purification_rounds(F_initial_2, required_thresh)
                


                p_p=purification_probability(F_initial)


                successful_purification_rounds=calculate_successful_purification_rounds(rounds, p_p)

                rounds_dizin.append(successful_purification_rounds)


                F_final_path, edge_final_fidelities = compute_path_final_fidelity(
                 G=G,
                 path=path,
                 alpha=alpha,
                 successful_purification_rounds=successful_purification_rounds,
                 default_distance_km=fixed_distance,
                 default_F_init=F_initial  # istersen sabit bir değer de verebilirsin
                )

      # Bell pair hesapla (rounds None olsa bile kontrol ederek)
                if successful_purification_rounds is not None:
                    bell_pairs = compute_required_bell_pairs(demand, successful_purification_rounds)
                else:
                    bell_pairs = None


                usable_cap = calculate_usable_capacity_for_path(G, path)
                t_ent_gen = calculate_total_entanglement_time(G, path, L_att)  
                
      

                t_purif=calculate_total_purification_time_from_path(G, path, successful_purification_rounds, F_initial_2, L_att, c_fiber=2e8)
                t_swap = calculate_swapping_time(G, path, c_fiber=2e8)
 

                L_total= (len(path) - 1)*L
                c_fiber=2e8
                total_time= t_ent_gen  +  t_purif + t_swap


                link_dist_m_list = []
                for u, v in zip(path[:-1], path[1:]):
                    if 'distance_km' in G[u][v]:
                      d_m = float(G[u][v]['distance_km']) * 1000.0
                    elif 'distance_m' in G[u][v]:
                       d_m = float(G[u][v]['distance_m'])
                    else:
                       d_m = float(fixed_distance) * 1000.0  # fallback: fixed_distance (km) -> m
                    link_dist_m_list.append(d_m)  # 

# --- 2) Her edge için AYNI tau_gen kullan (eşit paylaştırma yok) ---
                n_edges = max(1, len(link_dist_m_list))
                tau_gen_list = [t_ent_gen] * n_edges

# --- 3) EGR ortak parametreleri ---
                # --- EGR ortak sabitleri (p_ht hariç) ---
                base_common = {
    # 'p_ht' edge-bazlı gelecek!
                   'nu_h': 0.8, 'nu_t': 0.8, 'nu_o': 0.390,
                   'L0': 22_000.0, 'c_f': 2e8,
                   'tau_p': 5.9e-6, 'tau_h': 20e-6, 'tau_t': 10e-6, 'tau_o': 10e-6,
                   'tau_d': 100e-6, 'T_ch': 1
}

                default_p_ht = 0.53  # grafikte yoksa/fault durumunda kullanılacak

# --- Kenar listesini ve mesafeleri hazırla ---
                edges_on_path = list(zip(path[:-1], path[1:]))

                link_dist_m_list = []
                for u, v in edges_on_path:
                    if 'distance_m' in G[u][v]:
                      d_m = float(G[u][v]['distance_m'])
                    elif 'distance_km' in G[u][v]:
                      d_m = float(G[u][v]['distance_km']) * 1000.0
                    else:
                      d_m = float(fixed_distance) * 1000.0
                    link_dist_m_list.append(d_m)

                n_edges = max(1, len(edges_on_path))
                tau_gen_list = [0.0]*n_edges
                tau_gen_list[0] = t_ent_gen
                 
# --- Path’teki HER edge için p_ht'yi grafikten çekip link_params oluştur ---
                link_params_list = []
                for i, ((u, v), d_m, tau_gen_edge) in enumerate(zip(edges_on_path, link_dist_m_list, tau_gen_list)):
    # Grafikten p_ht (entanglement_prob) oku; yoksa default
                   p_ht_edge = G[u][v].get('entanglement_prob', default_p_ht)
    # Güvenlik: aralığa sıkıştır
                   try:
                      p_ht_edge = float(p_ht_edge)
                   except Exception:
                      p_ht_edge = default_p_ht
                   p_ht_edge = max(0.0, min(1.0, p_ht_edge))

    # Bu edge için common sözlüğü
                   common_edge = dict(base_common)
                   common_edge['p_ht'] = p_ht_edge

                   lp = egr.build_link_params(
                     common_edge,
                     d_ij=d_m,              # metre
        # L0=27_000.0,         # override etmek istersen aç
                     tau_gen=tau_gen_edge   # her edge için sabit tau_gen kullanıyoruz
        # tau_c_ij verilmezse otomatik d/(2 c_f)
    )
                   link_params_list.append(lp)

# --- Uçtan-uca (path) entanglement generation rate ---
                tau_a = 10e-6
                nu_a  = 0.9
                route_res = egr.compute_route_rate(link_params_list, tau_a=tau_a, nu_a=nu_a, T_ch=base_common['T_ch'])

                EGR_R   = route_res['R_route']
                EGR_TR  = route_res['T_R']
                EGR_tauR= route_res['tau_R']

# path_infos'a ekle (senin şemanla tam uyumlu)
                path_infos.append({
                 "path": path,
                 "intermediate_nodes": intermediate_nodes,
                 "required_threshold": required_thresh,
                 "purification_rounds": successful_purification_rounds,
                 "required_bell_pairs": bell_pairs,
                 "usable_capacity": usable_cap,
                 "t_swap": t_swap,
                 "F_final_edge_list": edge_final_fidelities,
                 "F_final_path": F_final_path,
                 "F_final": F_final_path,
                 "t_ent_gen": t_ent_gen,
                 "t_purif": t_purif,

    # --- EGR çıktıları ---
                 "EGR": route_res,          # tüm detaylar
                 "EGR_R_route": EGR_R,      # kısa erişim
                 "EGR_T_R": EGR_TR,
                 "EGR_tau_R": EGR_tauR,
                 "total_time": total_time,
                })



            all_path_info_per_request.append(path_infos)
            
            

            


            # (Burası all_path_info_per_request.append(path_infos) satırından SONRA olmalı)
# !!! sende yanlış yere kaymıştı; append() tek satır olmalı


# ---- C_real’i her path için ekle ----
        for req_idx, paths_of_req in enumerate(all_path_info_per_request):
            G = G_per_request[req_idx]

            for p_idx, path_info in enumerate(paths_of_req):
                path = path_info["path"]

        # 1) M ve X
                M = path_info.get("purification_rounds")
                M_use = int(M) 
                #M_use=M_used
                # X ve L_path_km:
                X = len(path) - 1
                L_path_km = path_length_km_from_graph(G, path, default_fixed_distance_km=fixed_distance)

               

                # C_real( FE2E_required ) — total_time YOK, FE2E ekseninde interp
                C_req, L_used, st, dbg = get_C_real_at_required_FE2E(
                 lookup_df=lookup_df_real,
                 M=M, X=X, L_km= fixed_distance , FE2E_required=F_final_path,
                 C_col_override="C_real",
                 out_of_range="nan",                 # dilim içinde aralık dışı ise None
                 fe2e_policy="clip_intersection",    # L0-L1 kesişimine kırp
                 cmin=0.0, cmax=1.0,
                 debug=True
                )
                print(st)   # burada "fe2e_clipped_to_intersection[...]" gibi net mesaj göreceksin
                path_info["C_real_at_required"] = C_req

                C_real=C_req
                path_info["C_real_status"] = st
                path_info["L_used_for_C"]  = L_used
                        # coherence_values listesine sadece geçerli sayı ekle
                if _is_num(C_real):
                    coherence_values.append(float(C_real))

        # ayrıca all_path_info_per_request’e geri yaz (sende bunu yapıyorsun)
                all_path_info_per_request[req_idx][p_idx]['C_real'] = C_real
                #all_path_info_per_request[req_idx][p_idx]['matched_FE2E'] = matched_FE2E
                all_path_info_per_request[req_idx][p_idx]['lookup_status'] = st
                all_path_info_per_request[req_idx][p_idx]['C_rel_ent'] = C_real  # <--- önemli



        success_count = 0
        drop_count_capacity = 0
        drop_count_crel = 0
        drop_count_egr = 0
        drop_count_time = 0
        drop_count_fid=0
        drop_count_link_fail = 0

        time_limit = 0.001 # saniye sınırı

        for req_index, path_infos in enumerate(all_path_info_per_request):
            request = df_sorted.iloc[req_index]
            f_threshold = float(request['f_threshold'])

            
            best_path, backup_path, stats = select_best_and_backup_paths(
            path_infos=path_infos,
            C_rel_th=Crel_th,
            overlap_mode="edge",
            return_stats=True,
            debug=False
            )

    # Karar sınıflandırması (drop nedenlerini sayaçla ve devam etme)
            if stats["decision"] != "ok":
                reason = stats["decision"]  # "drop_capacity" | "drop_crel" | "drop_egr"
                if reason == "drop_capacity":
                    drop_count_capacity += 1
                    print(f"🔷 Request {req_index}: dropped by CAPACITY (uc<rbp veya rbp eksik).")
                elif reason == "drop_crel":
                    drop_count_crel += 1
                    print(f"🔷 Request {req_index}: dropped by C_rel (threshold={Crel_th}).")
                elif reason == "drop_egr":
                    drop_count_egr += 1
                    print(f"🔷 Request {req_index}: dropped by EGR (None/missing).")
        # Drop’larda ortalama metrikleri BOZMAMAK için Latency/final_fidelity eklemiyoruz.
                continue  # <-- BU SATIR TÜM DROP NEDENLERİ İÇİN GEÇERLİ

    # (Opsiyonel) Ek güvenlik: normalde buraya düşmez
           

    # ----- Buradan sonrası sadece decision="ok" için -----
            G = G_per_request[req_index]
            fail_fidelity = 0.5
            G_updated, failed_edges = add_link_failures_by_percentage(
            G, failure_percentage=0.0, fail_fidelity=fail_fidelity
            )

            min_fidelity = 0.49
            valid_path, used_backup = check_and_select_valid_path(G_updated, best_path, backup_path, min_fidelity)
            
            if not valid_path:
             drop_count_link_fail += 1
             continue

            arr = float(request["arrival_time"])
            lev = float(request["leave_time"])

            path_chosen = valid_path["path"]
            edges_new = set(zip(path_chosen[:-1], path_chosen[1:]))

            conflict = False
            for (a0, b0, e0) in accepted_reservations:
                if overlap_frac(arr, lev, a0, b0) >= overlap_th:
                    if edges_new & e0:
                        conflict = True
                        break

            if conflict:
                drop_count_overlap += 1
                continue
            else:
                accepted_reservations.append((arr, lev, edges_new))



            if valid_path:
                t_ent_gen = valid_path.get("t_ent_gen")
                t_swapping = valid_path.get("t_swap")
                t_purif   = valid_path.get("t_purif")
                t_total   = t_ent_gen + t_swapping + t_purif
                path_chosen = valid_path.get("path", None)
                if path_chosen is not None:
                    hop_count = len(path_chosen) - 1
                    # toplam yol uzunluğunu km cinsinden hesapla
                    L_path_km = path_length_km_from_graph(
                        G_updated, 
                        path_chosen, 
                        default_fixed_distance_km=fixed_distance
                    )
                else:
                    # path yoksa, en azından hop sayısını bilmiyoruz, NaN koyarız
                    hop_count = float('nan')
                    L_path_km = float('nan')

                # --- YENİ: makale için global per-request metriklere ekle ---
                all_req_rounds.append(valid_path.get("purification_rounds", float('nan')))
                all_req_latency.append(t_total)
                all_req_t_ent.append(t_ent_gen)
                all_req_t_purif.append(t_purif)
                all_req_t_swap.append(t_swapping)
                all_req_path_hops.append(hop_count)
                all_req_path_len_km.append(L_path_km)
                all_req_freq.append(freq_for_capacity)

                Latency =  t_total
                Latency_dizin.append(Latency)

                final_fidelity = valid_path.get("F_final")
                final_fidelities.append(final_fidelity)

                print(f"\n🔷 Request {req_index}")
                print(f"   🕒 t_total = {t_total:.4e} s (ent + swap + purif)")
                print(f"   📈 final_fidelity = {final_fidelity:.4f} | threshold = {f_threshold:.4f}")

                C_x = valid_path.get("C_real")
                if (t_total <= time_limit) and (final_fidelity >= f_threshold) and ( C_x >= Crel_th):
                    print("   ✔️ Request SUCCESSFUL (time)")
                    success_count += 1
                    c_ok = valid_path.get("C_real", None)
                    if isinstance(c_ok, (int, float)) and np.isfinite(c_ok):
                        success_coherences_all.append(float(c_ok))
                elif t_total > time_limit:
                    drop_count_time += 1
                elif   final_fidelity < f_threshold:
                    drop_count_fid += 1
            else:
                print(f"   ⚠️ Request {req_index}: No valid path after link failure.")
                drop_count_link_fail += 1
        # Drop’larda Latency eklemiyoruz; istersen np.nan ekleyip np.nanmean kullan.

 

        total_requests = NUM_REQ

        success_rate          = 100.0 * success_count          / total_requests
        drop_rate_capacity    = 100.0 * drop_count_capacity    / total_requests
        drop_rate_crel        = 100.0 * drop_count_crel        / total_requests
        drop_rate_egr         = 100.0 * drop_count_egr         / total_requests
        drop_rate_time        = 100.0 * drop_count_time        / total_requests
        drop_rate_link_fail   = 100.0 * drop_count_link_fail   / total_requests
        drop_rate_fid         =  100.0 * drop_count_fid   / total_requests
        drop_rate_total       = 100.0 - success_rate
        


        success_rates.append(success_rate)
        drop_rates.append(drop_rate_total)

# kategori bazlı listeler (bu listeleri sabit başta tanımlıyorsun; bkz. aşağıdaki not)
        drop_rates_capacity.append(drop_rate_capacity)
        drop_rates_crel.append(drop_rate_crel)
        drop_rates_egr.append(drop_rate_egr)
        drop_rates_time.append(drop_rate_time)
        drop_rates_link_fail.append(drop_rate_link_fail)
        drop_rates_fid.append(drop_rate_fid)


# --- tekrarlardan (repetition) ortalama al ve üst düzey dizilere koy ---
    def _mean_or_nan(a):
            return float(np.mean(a)) if len(a) > 0 else float('nan')

    avg_success   = _mean_or_nan(success_rates)
        

    avg_fid       = _mean_or_nan(final_fidelities)
        

    avg_Latency   = _mean_or_nan(Latency_dizin)
       
    avg_coherence = _mean_or_nan(coherence_values)
        

    avg_S_coherence = _mean_or_nan(success_coherences_all)
        

    avg_rounds    = _mean_or_nan(rounds_dizin)
        


    A_req_rounds=_mean_or_nan(all_req_rounds)
    A_req_latency=_mean_or_nan(all_req_latency)
    A_req_t_ent=_mean_or_nan(all_req_t_ent)
    A_req_t_purif=_mean_or_nan(all_req_t_purif)
    A_req_t_swap=_mean_or_nan(all_req_t_swap)
    A_req_path_hops=_mean_or_nan(all_req_path_hops)
    A_req_path_len_km=_mean_or_nan(all_req_path_len_km)





    avg_drop_capacity   = _mean_or_nan(drop_rates_capacity)
    avg_drop_crel       = _mean_or_nan(drop_rates_crel)
    avg_drop_egr        = _mean_or_nan(drop_rates_egr)
    avg_drop_time       = _mean_or_nan(drop_rates_time)
    avg_drop_link_fail  = _mean_or_nan(drop_rates_link_fail)
    avg_drop_total      = _mean_or_nan(drop_rates)
    avg_drop_fid        = _mean_or_nan(drop_rates_fid)
    avg_rounds_needed = _mean_or_nan(rounds_needed_dizin)
    
  
    all_avg_success_rates.append(avg_success)
    all_avg_fidelities.append(avg_fid)
    all_avg_S_coherence_values.append(avg_S_coherence)
    all_avg_Latency.append(avg_Latency)
    all_avg_rounds.append(avg_rounds)
    all_avg_drop_capacity.append(avg_drop_capacity)
    all_avg_drop_crel.append(avg_drop_crel)
    all_avg_drop_egr.append(avg_drop_egr)
    all_avg_drop_time.append(avg_drop_time)
    all_avg_drop_link_fail.append(avg_drop_link_fail)
    all_avg_drop_total.append(avg_drop_total)
    all_avg_drop_fid.append(avg_drop_fid)
    all_avg_rounds_needed.append(avg_rounds_needed)
    all_avg_coherence_values.append(avg_coherence)

    All_req_rounds.append(A_req_rounds)
    All_req_latency.append(A_req_latency)
    All_req_t_ent.append(A_req_t_ent)
    All_req_t_purif.append(A_req_t_purif)
    All_req_t_swap.append(A_req_t_swap)
    All_req_path_hops.append(A_req_path_hops)
    All_req_path_len_km.append(A_req_path_len_km)
    

# --- Success rate ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_success_rates, marker='o', label='Average Success Rate (%)', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average Success Rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Final fidelity ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_fidelities, marker='x', label='Average Final Fidelity', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average Final Fidelity")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Coherence (all vs successful) ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_coherence_values, marker='x', label='Avg C_rel (all)', linewidth=2)
plt.plot(NUM_REQ_list, all_avg_S_coherence_values, marker='o', label='Avg C_rel (successful)', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average Coherence values")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Latency ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_Latency, marker='x', label='Average Latency with Purification', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average Latency (s)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Purification rounds ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_rounds , marker='x', label='Average purification rounds', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average rounds")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Total drop rate ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_total, marker='x', label='Average total drop rate (%)', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Drop by categories ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_capacity,   marker='x', label='Drop: Capacity (%)', linewidth=2)
plt.plot(NUM_REQ_list, all_avg_drop_crel,       marker='x', label='Drop: C_rel (%)', linewidth=2)
plt.plot(NUM_REQ_list, all_avg_drop_egr,        marker='x', label='Drop: EGR (%)', linewidth=2)
plt.plot(NUM_REQ_list, all_avg_drop_time,       marker='x', label='Drop: Time (%)', linewidth=2)
plt.plot(NUM_REQ_list, all_avg_drop_link_fail,  marker='x', label='Drop: Link failure (%)', linewidth=2)
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate by reason (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()


# --- Drop: Capacity ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_capacity, marker='x', linewidth=2, label='Drop: Capacity (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Drop: C_rel ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_crel, marker='x', linewidth=2, label='Drop: C_rel (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Drop: EGR ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_egr, marker='x', linewidth=2, label='Drop: EGR (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Drop: Time ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_time, marker='x', linewidth=2, label='Drop: Time (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# --- Drop: Link failure ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_link_fail, marker='x', linewidth=2, label='Drop: Link failure (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()


# --- Drop: Link failure ---
plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_drop_fid, marker='x', linewidth=2, label='Drop: fid (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("Average drop rate (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()




plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, all_avg_rounds_needed, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Fixed Distance (km)")
plt.ylabel("needed rounds (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()


plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, All_req_path_hops, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Capacity (km)")
plt.ylabel("number of hops (%)")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()



plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, All_req_path_len_km, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Capacity (km)")
plt.ylabel("Path length km ")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()




plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, All_req_t_swap, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Capacity (km)")
plt.ylabel("swapping time ")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()



plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, All_req_t_ent, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Capacity (km)")
plt.ylabel("ent gen time ")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()


plt.figure(figsize=(10, 6))
plt.plot(NUM_REQ_list, All_req_t_purif, marker='x', linewidth=2, label='needed rounds (%)')
plt.xlabel("Capacity (km)")
plt.ylabel("purif time ")
plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()







import numpy as np
from pathlib import Path

def save_results_npz(
    NUM_REQ_list,
    all_avg_success_rates,
    all_avg_fidelities,
    all_avg_coherence_values,
    all_avg_S_coherence_values,   # <-- eklendi (successful-only)
    all_avg_Latency,
    all_avg_rounds,
    all_avg_drop_capacity,        # <-- yeni
    all_avg_drop_crel,            # <-- yeni
    all_avg_drop_egr,             # <-- yeni
    all_avg_drop_time,
    all_avg_drop_link_fail,
    all_avg_drop_total,
    all_avg_drop_fid,
    All_req_path_hops,
    All_req_path_len_km,
    All_req_t_swap,
    All_req_t_ent,
    All_req_t_purif,
    out_path="REQ_YC_FTH_C_TH08_C100_Node10_npz/REQ1_metrics.npz"
):
    """
    Sonuç dizilerini tek bir .npz içinde saklar (sıkıştırmalı).
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        out_path,
        NUM_REQ_L=np.asarray(NUM_REQ_list, dtype=float),
        avg_success_rates=np.asarray(all_avg_success_rates, dtype=float),
        avg_fidelities=np.asarray(all_avg_fidelities, dtype=float),
        avg_coherence_values=np.asarray(all_avg_coherence_values, dtype=float),
        avg_coherence_success_values=np.asarray(all_avg_S_coherence_values, dtype=float),
        avg_latency=np.asarray(all_avg_Latency, dtype=float),
        avg_rounds=np.asarray(all_avg_rounds, dtype=float),
        avg_hops=np.asarray(All_req_path_hops, dtype=float),
        avg_length=np.asarray(All_req_path_len_km, dtype=float),
        avg_swappin_t=np.asarray(All_req_t_swap, dtype=float),
        avg_ent_gen_t=np.asarray(All_req_t_ent, dtype=float),
        avg_purif_t=np.asarray(All_req_t_purif, dtype=float),


        # drop kategorileri
        avg_drop_capacity=np.asarray(all_avg_drop_capacity, dtype=float),
        avg_drop_crel=np.asarray(all_avg_drop_crel, dtype=float),
        avg_drop_egr=np.asarray(all_avg_drop_egr, dtype=float),
        avg_drop_time=np.asarray(all_avg_drop_time, dtype=float),
        avg_drop_link_fail=np.asarray(all_avg_drop_link_fail, dtype=float),
        avg_drop_total=np.asarray(all_avg_drop_total, dtype=float),
        avg_drop_fid=np.asarray(all_avg_drop_fid, dtype=float),






    )
    print(f"[✓] Kaydedildi: {Path(out_path).resolve()}")

save_results_npz(
    NUM_REQ_list,
    all_avg_success_rates,
    all_avg_fidelities,
    all_avg_coherence_values,
    all_avg_S_coherence_values,   # başarılı isteklerin C_rel ortalaması
    all_avg_Latency,
    all_avg_rounds,
    all_avg_drop_capacity,
    all_avg_drop_crel,
    all_avg_drop_egr,
    all_avg_drop_time,
    all_avg_drop_link_fail,
    all_avg_drop_total,
    all_avg_drop_fid,
    All_req_path_hops,
    All_req_path_len_km,
    All_req_t_swap,
    All_req_t_ent,
    All_req_t_purif,
    out_path="REQ_YC_FTH_C_TH08_C100_Node10_npz/REQ1_metrics.npz"
)






