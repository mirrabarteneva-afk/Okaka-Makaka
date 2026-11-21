import pandas as pd
from pathlib import Path

def get_headers(file_path: Path, delim=',') -> list[str]:
    try:
        df = pd.read_csv(file_path, delimiter=delim, encoding='UTF-8')
        return [col for col in df.columns]
    except Exception as e:
        return []