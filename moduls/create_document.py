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
