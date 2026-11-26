import numpy as np


def get_table_data(table, header, selected_names):
    cols = [header.index(name) for name in selected_names]
    rows = table.rowCount()
    data = np.full((rows, len(cols)), np.nan)
    for i in range(rows):
        for k, col in enumerate(cols):
            item = table.item(i, col)
            if item is None:
                continue
            try:
                data[i, k] = float(item.text())
            except ValueError:
                pass
    return data

def make_diverging_lut(n=256):
    lo = np.array([178, 34, 34], dtype=float)
    mid = np.array([255, 255, 255], dtype=float)
    hi = np.array([30, 144, 255], dtype=float)   # синий — положительная связь
    lut = np.empty((n, 3), dtype=np.ubyte)
    half = n // 2
    for i in range(half):
        t = i / max(half - 1, 1)
        lut[i] = (mid + (lo - mid) * t).astype(np.ubyte)
    for i in range(half, n):
        t = (i - half) / max(n - half - 1, 1)
        lut[i] = (mid + (hi - mid) * t).astype(np.ubyte)
    return lut
