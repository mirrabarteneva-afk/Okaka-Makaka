def sr_valye(numbers_sorted):
    try:
        sr_number = sum(numbers_sorted) / len(numbers_sorted)
        return sr_number
    
    except Exception:
        return