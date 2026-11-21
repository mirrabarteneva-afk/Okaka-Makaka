import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
csv_path = base_dir / "test.csv"
columns = ['name', 'grade']

with open(csv_path, 'r', newline='', encoding='utf-8') as file:
    data = csv.reader(file, delimiter=',')
    headers = next(data)
    headers_for_table = [headers.index(x) for x in list(filter(lambda x: x in columns, headers))]
    data_lst = list(data)
    data = [(x[1], x[3]) for x in data_lst]
    print(data)