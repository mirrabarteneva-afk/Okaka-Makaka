import sqlite3 as sql
from pathlib import Path


def db_table_create(columns: list, path: Path, table_name: str) -> tuple:
    try:
        with sql.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'PRAGMA table_info({table_name})')
            exitinc = [c[1] for c in cursor.fetchall()]
            headers = [x for x in columns if x in exitinc]
            cols = ', '.join(headers)
            if cols and table_name:
                cursor.execute(f'SELECT {cols} FROM {table_name}')
                data_list = cursor.fetchall()
                return (headers, data_list)
    except Exception:
        return