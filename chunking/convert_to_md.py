import os 
from tqdm import tqdm
from pprint import pprint
import pdfplumber
from markdownify import markdownify

def clean_table(table):
    tranposed_table = list(zip(*table))
    keep = [
        idx for idx,col in enumerate(tranposed_table)
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
        cleaned_row = [str(cell).strip() if cell is not None else '' for cell in row]
        res.append('| ' + ' | '.join(cleaned_row) + ' |')
        if i == 0:
            res.append('| ' + ' | '.join(['---'] * len(cleaned_row)) + ' |')
    return '\n'.join(res)

def process_tables(tables):
    md_tables = []
    for table in tables:
        if not table or len(table) < 1: continue
        
        length = set()
        cleaned_table = clean_table(table)
        md_table = table2markdown(cleaned_table)
    md_tables.append(md_table)


def convert_to_markdown(pdf_path, md_path):
    loop = tqdm(os.listdir(pdf_path),desc='Converting PDFs', unit='file')
    for file in loop:
        file_path = os.path.join(pdf_path,file)
        md_path = os.path.join(md_path, file_path.replace('.pdf','.md'))
        
        md_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                md_tables = process_tables(tables)
                
                    

convert_to_markdown('docs', 'md')