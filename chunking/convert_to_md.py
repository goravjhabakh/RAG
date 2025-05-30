import os
from tqdm import tqdm
import pdfplumber
from markdownify import markdownify

def clean_table(table):
    transposed_table = list(zip(*table))
    keep = [
        idx for idx, col in enumerate(transposed_table)
        if any(cell and str(cell).strip() for cell in col)
    ]
    cleaned_table = [
        [row[idx] if idx < len(row) else "" for idx in keep]
        for row in table
    ]
    return cleaned_table

def table2markdown(table):
    res = []
    for i, row in enumerate(table):
        cleaned_row = [str(cell).strip() if cell else '' for cell in row]
        res.append('| ' + ' | '.join(cleaned_row) + ' |')
        if i == 0:
            res.append('| ' + ' | '.join(['---'] * len(cleaned_row)) + ' |')
    return '\n'.join(res)

def process_tables(tables):
    md_tables = []
    for table in tables:
        if not table or len(table) < 1:
            continue
        cleaned = clean_table(table)
        md = table2markdown(cleaned)
        md_tables.append(md)
    return md_tables

def extract_proper_text(page):
    boxes = [table.bbox for table in page.find_tables() if table.bbox]

    def outside_table(char):
        for x0, top, x1, bottom in boxes:
            if x0 <= char['x0'] <= x1 and top <= char['top'] <= bottom:
                return False
        return True

    chars = [char for char in page.chars if outside_table(char)]
    return pdfplumber.utils.extract_text(chars) if chars else ''

def convert_to_markdown(pdf_dir, md_dir):
    md_output = {}

    for file in tqdm(os.listdir(pdf_dir), desc='Converting PDFs', unit='file'):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_dir, file)
        file_output = {}

        with pdfplumber.open(file_path) as pdf:
            for pg_no, page in enumerate(pdf.pages, start=1):
                text = extract_proper_text(page)
                tables = page.extract_tables()
                md_tables = process_tables(tables)

                file_output[f"page_{pg_no}"] = {
                    "text": text,
                    "tables": md_tables
                }

        md_output[file] = file_output

    return md_output

md_content = convert_to_markdown('docs', 'md')