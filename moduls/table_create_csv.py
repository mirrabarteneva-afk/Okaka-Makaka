import pandas as pd
from pathlib import Path
from moduls.mask import apply

def csv_table_create(columns: list, path: Path, delim: str, conditions=None) -> tuple:
    try:
        df = pd.read_csv(path, delimiter=delim, encoding='utf-8')
        
    except FileNotFoundError:
        return (columns, [])
    

    found = [col for col in columns if col in df.columns]
    headers = found

    if not conditions:
        return (headers, df[found].values.tolist())


    masks = []
    ops = []

    for item in conditions:
        if isinstance(item, str):
            if item not in ('AND', 'OR'):
                return

            ops.append(item)

        else:
            column, oper, cond = item

            if column == 'Нет':
                return

            masks.append(apply(df, column, oper, cond))

    if len(masks) != len(ops) + 1:
        return

    mask = masks[0]
    
    for op, m in zip(ops, masks[1:]):
        print('  проходит строк:', int(m.sum()))
        mask = mask & m if op == 'AND' else mask | m

    return (headers, df.loc[mask, found].values.tolist())