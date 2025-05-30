import pandas as pd
from converters.base import BaseDocumentConverter
from typing import Dict

class ExcelToMarkdownConverter(BaseDocumentConverter):
    def convert(self, file_path: str) -> Dict[str, str]:
        excel = pd.ExcelFile(file_path)
        result = {}
        for sheet in excel.sheet_names:
            df = excel.parse(sheet)
            result[sheet] = df.to_markdown(index=False)
        return result
    
