import pandas as pd

def save_table(file, format, data):

    if 'CSV' in format and file.lower().endswith('.csv'):
        df = pd.read_csv(file)
        df.to_csv(file, index=False, sep=',', encoding='utf-8')