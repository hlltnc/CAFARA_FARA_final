import numpy as np
import pandas as pd

def _detect_time_cols(df: pd.DataFrame):
    """
    df içinden arrival/leave kolonlarını bulmaya çalışır.
    Kendi generate_requests fonksiyonundaki kolon isimleri farklıysa buraya ekleyin.
    """
    candidates = [
        ("arrival_time", "leave_time"),
        ("arrival", "leave"),
        ("t_arrival", "t_leave"),
        ("start_time", "end_time"),
        ("t_start", "t_end"),
        ("arrive", "depart"),
    ]
    cols = set(df.columns)
    for a, b in candidates:
        if a in cols and b in cols:
            return a, b
    raise KeyError(
        f"Arrival/leave kolonları bulunamadı. Mevcut kolonlar: {list(df.columns)}. "
        "Lütfen _detect_time_cols içindeki aday listeye kendi kolon isimlerinizi ekleyin."
    )

def drop_late_requests_by_overlap(
    df: pd.DataFrame,
    overlap_threshold: float = 0.50,
    arrival_col: str | None = None,
    leave_col: str | None = None,
):
    """
    Zaman aralığı örtüşmesi >= overlap_threshold olan SONRADAN GELEN request'i drop eder.
    Overlap oranı: overlap_duration / duration(new_request)

    Döndürür:
      df_kept: tutulacak requestler (reset_index yapılmış)
      n_dropped: drop edilen request sayısı
      df_marked: tüm requestler + drop_by_overlap flag
    """
    if arrival_col is None or leave_col is None:
        arrival_col, leave_col = _detect_time_cols(df)

    df2 = df.sort_values(arrival_col).reset_index(drop=True).copy()
    drop_flags = np.zeros(len(df2), dtype=bool)

    accepted_intervals = []  # [(a,b), ...]

    for i, row in df2.iterrows():
        a = float(row[arrival_col])
        b = float(row[leave_col])

        # Güvenlik: hatalı/ters aralıklar
        if not np.isfinite(a) or not np.isfinite(b) or b <= a:
            # İsterseniz burada direkt drop da edebilirsiniz; ben "tut" varsaydım
            accepted_intervals.append((a, b))
            continue

        dur_new = b - a
        should_drop = False

        for (a0, b0) in accepted_intervals:
            # Overlap süresi
            ov = max(0.0, min(b, b0) - max(a, a0))
            if ov / dur_new >= overlap_threshold:
                should_drop = True
                break

        if should_drop:
            drop_flags[i] = True
        else:
            accepted_intervals.append((a, b))

    df2["drop_by_overlap"] = drop_flags
    n_dropped = int(drop_flags.sum())
    df_kept = df2.loc[~df2["drop_by_overlap"]].reset_index(drop=True)

    return df_kept, n_dropped, df2
