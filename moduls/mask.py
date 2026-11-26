def parse_range(value:str):
    value = str(value).strip()

    for sep in [';', ':', ', ']:
        if sep in value:
            parts = value.split(sep)
            break

        else:
            parts = value.split()

        if len(parts) != 2:
            return
        
    return float(parts[0]), float(parts[1])

def apply(df, column, oper, cond):
    if oper == '=':
        try:
            cond = float(cond)

        except ValueError:
            cond = str(cond)

        return df[column] == cond

    if oper == '>':
        cond = float(cond)
        return df[column] > cond

    if oper == '<':
        cond = float(cond)
        return df[column] < cond

    if oper == '>=':
        cond = float(cond)
        return df[column] >= cond

    if oper == '<=':
        cond = float(cond)
        return df[column] <= cond
        
    if oper == 'Диапазон вкл':
        x, x1 = parse_range(cond)
        return df[column].between(x, x1, inclusive='both')

    if oper == 'Диапазон не вкл':
        x, x1 = parse_range(cond)
        return df[column].between(x, x1, inclusive=False)

    if oper == 'В тексте':
        return df[column].astype(str).str.contains(str(cond), case=False, na=False)

    if oper == 'Пусто':
        return df[column].isna() | (df[column].astype(str).str.strip() == '')

    if oper == 'Не пусто':
        return df[column].notna() & (df[column].astype(str).str.strip() != '')
    
    return None