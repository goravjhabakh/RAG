import os
from typing import List, Dict
import pdfplumber
from tqdm import tqdm
from converters.base import BaseDocumentConverter

class PDFToMarkdownConverter(BaseDocumentConverter):
    def __init__(self, pdf_dir: str, md_dir: str):
        self.pdf_dir = pdf_dir
        self.md_dir = md_dir

    def convert(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        md_output = {}

        for file in tqdm(os.listdir(self.pdf_dir), desc='Converting PDFs...', unit='file(s)'):
            if not file.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(self.pdf_dir, file)
            file_output = self._convert_single_pdf(file_path)
            md_output[file] = file_output

        return md_output

    def _convert_single_pdf(self, file_path: str) -> Dict[str, Dict[str, List[str]]]:
        output = {}
        with pdfplumber.open(file_path) as pdf:
            for pg_no, page in enumerate(pdf.pages, start=1):
                text = self._extract_proper_text(page)
                tables = page.extract_tables()
                md_tables = self._process_tables(tables)

                output[f"page_{pg_no}"] = {
                    "text": text,
                    "tables": md_tables
                }
        return output

    def _extract_proper_text(self, page) -> str:
        boxes = [table.bbox for table in page.find_tables() if table.bbox]

        def outside_table(char):
            for x0, top, x1, bottom in boxes:
                if x0 <= char['x0'] <= x1 and top <= char['top'] <= bottom:
                    return False
            return True

        chars = [char for char in page.chars if outside_table(char)]
        return pdfplumber.utils.extract_text(chars) if chars else ''

    def _process_tables(self, tables) -> List[str]:
        return [
            self._table_to_markdown(self._clean_table(table))
            for table in tables if table and len(table) > 0
        ]

    def _clean_table(self, table):
        transposed = list(zip(*table))
        keep = [
            idx for idx, col in enumerate(transposed)
            if any(cell and str(cell).strip() for cell in col)
        ]
        return [
            [row[idx] if idx < len(row) else "" for idx in keep]
            for row in table
        ]

    def _table_to_markdown(self, table) -> str:
        res = []
        for i, row in enumerate(table):
            cleaned = [str(cell).strip() if cell else '' for cell in row]
            res.append('| ' + ' | '.join(cleaned) + ' |')
            if i == 0:
                res.append('| ' + ' | '.join(['---'] * len(cleaned)) + ' |')
        return '\n'.join(res)
    
converter = PDFToMarkdownConverter('../chunking/docs','../chunking/md')
print(converter.convert())