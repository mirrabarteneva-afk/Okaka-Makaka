import sqlite3

def parse_range(value: str):
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

def build_where(conditions, prefix=''):
    if not conditions:
        return '', {}
    parts = []
    params = {}
    ops = []
    i = 0
    for item in conditions:
        if isinstance(item, str):
            if item not in ('AND', 'OR'):
                return None
            ops.append(item)
            continue
        column, oper, cond = item
        if column == 'Нет':
            return None
        i += 1
        col = f'"{column}"'
        k = f'{prefix}p{i}'
        k2 = f'{prefix}p{i}_2'
        if oper == '=':
            try:
                cond = float(cond)
            except (ValueError, TypeError):
                pass
            parts.append(f'{col} = :{k}')
            params[k] = cond
        elif oper == '>':
            try:
                params[k] = float(cond)
            except (ValueError, TypeError):
                return None
            parts.append(f'{col} > :{k}')
        elif oper == '<':
            try:
                params[k] = float(cond)
            except (ValueError, TypeError):
                return None
            parts.append(f'{col} < :{k}')
        elif oper == '>=':
            try:
                params[k] = float(cond)
            except (ValueError, TypeError):
                return None
            parts.append(f'{col} >= :{k}')
        elif oper == '<=':
            try:
                params[k] = float(cond)
            except (ValueError, TypeError):
                return None
            parts.append(f'{col} <= :{k}')
        elif oper == 'Диапазон вкл':
            rng = parse_range(cond)
            if rng is None:
                return None
            parts.append(f'{col} BETWEEN :{k} AND :{k2}')
            params[k], params[k2] = rng
        elif oper == 'Диапазон не вкл':
            rng = parse_range(cond)
            if rng is None:
                return None
            parts.append(f'({col} > :{k} AND {col} < :{k2})')
            params[k], params[k2] = rng
        elif oper == 'В тексте':
            val = str(cond)
            val = val.replace('\\', '\\\\').replace('%', r'\%').replace('_', r'\_')
            parts.append(f"{col} LIKE :{k} ESCAPE '\\'")
            params[k] = f'%{val}%'
        elif oper == 'Пусто':
            parts.append(f"({col} IS NULL OR TRIM(CAST({col} AS TEXT)) = '')")
        elif oper == 'Не пусто':
            parts.append(f"({col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) != '')")
        else:
            return None
    if len(parts) != len(ops) + 1:
        return None
    where = parts[0]
    for op, part in zip(ops, parts[1:]):
        where += f' {op} {part}'
    return where, params
