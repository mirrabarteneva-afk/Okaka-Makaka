import sqlite3
from pathlib import Path
from moduls.sql_mask import build_where


def sql_table_create(columns: list, db_path: Path, table: str, conditions=None) -> tuple:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f'PRAGMA table_info("{table}")')
        table_cols = [row[1] for row in cur.fetchall()]

    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return (columns, [])

    if not table_cols:
        conn.close()
        return (columns, [])

    found = [col for col in columns if col in table_cols]
    headers = found

    if not conditions:
        sel = ', '.join(f'"{c}"' for c in headers) or '*'
        cur.execute(f'SELECT {sel} FROM "{table}"')
        rows = [list(row) for row in cur.fetchall()]
        conn.close()
        return (headers, rows)

    masks_sql = []
    masks_params = []
    ops = []

    for item in conditions:
        if isinstance(item, str):
            if item not in ('AND', 'OR'):
                conn.close()
                return

            ops.append(item)

        else:
            column, oper, cond = item

            if column == 'Нет':
                conn.close()
                return

            built = build_where([(column, oper, cond)], prefix=f'c{len(masks_sql)}_')
            if built is None:
                conn.close()
                return

            sql, params = built
            masks_sql.append(sql)
            masks_params.append(params)

    if len(masks_sql) != len(ops) + 1:
        conn.close()
        return

    where = masks_sql[0]
    all_params = {}

    for op, sql, params in zip(ops, masks_sql[1:], masks_params[1:]):
        cur.execute(f'SELECT COUNT(*) FROM "{table}" WHERE {sql}', params)
        print('  проходит строк:', int(cur.fetchone()[0]))
        where += f' {op} {sql}'

    for params in masks_params:
        all_params.update(params)

    sel = ', '.join(f'"{c}"' for c in headers) or '*'
    cur.execute(f'SELECT {sel} FROM "{table}" WHERE {where}', all_params)
    rows = [list(row) for row in cur.fetchall()]
    conn.close()

    return (headers, rows)

