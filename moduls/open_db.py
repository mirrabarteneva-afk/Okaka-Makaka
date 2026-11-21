import sqlite3
import pandas as pd
from pathlib import Path


def get_headers_column(path: Path, table_name) -> list:
    if table_name:
        with sqlite3.connect(path) as db:
            cursor = db.cursor()
            try:
                cursor.execute(f'PRAGMA table_info({table_name})')
                return [row[1] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                return
    else:
        return
