import pandas as pd
import sqlite3
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def create_file(
        table_widget,
        path_for_document: Path,
        text:str,
        ):

    doc = Document()
    doc.add_heading('Отчёт по данным', level=0)

    rows = table_widget.rowCount()
    columns = table_widget.columnCount()

    doc_table = doc.add_table(rows=rows, cols=columns)
    doc_table.style = 'Table Grid'

    for i in range(rows):
        for j in range(columns):
            item = table_widget.item(i, j)
            doc_table.cell(i, j).text = item.text() if item is not None else ''

    for cell in doc_table.rows[0].cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(12)

    

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.add_run(text)

    doc.save(path_for_document)


def create_file_table(table_widget, path_for_document, format, table_name=None):
    if format == '.csv':
        rows = table_widget.rowCount()
        columns = table_widget.columnCount()

        headers = []
        for j in range(columns):
            item = table_widget.horizontalHeaderItem(j)
            headers.append(item.text() if item else f'col_{j}')

        data = []
        for i in range(rows):
            row = []
            for j in range(columns):
                item = table_widget.item(i, j)
                row.append(item.text() if item else '')
            data.append(row)

        df = pd.DataFrame(data, columns=headers)
        df.to_csv(path_for_document, index=False, sep=';', encoding='utf-8-sig')


    if format == '.db':
        conn = sqlite3.connect(path_for_document)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
            cur = conn.cursor()

            columns = table_widget.columnCount()

            headers = []
            for j in range(columns):
                item = table_widget.horizontalHeaderItem(j)
                headers.append(item.text() if item else f'col_{j}')

            safe_headers = [f'"{h}"' for h in headers]

            col_defs = ',\n    '.join(f'{h} TEXT' for h in safe_headers)
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {col_defs}
                )
            ''')

            placeholders = ', '.join('?' for _ in headers)
            cols_str = ', '.join(safe_headers)
            insert_sql = f'INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})'

            rows_data = []
            for i in range(table_widget.rowCount()):
                row = []
                for j in range(columns):
                    item = table_widget.item(i, j)
                    row.append(item.text() if item else None)
                rows_data.append(row)

            cur.executemany(insert_sql, rows_data)

            conn.commit()
        finally:
            conn.close()