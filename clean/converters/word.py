from docx import Document
from converters.base import BaseDocumentConverter
from typing import Dict

class WordToMarkdownConverter(BaseDocumentConverter):
    def convert(self, file_path: str) -> Dict[str, str]:
        doc = Document(file_path)
        content = []
        for para in doc.paragraphs:
            content.append(para.text.strip())
        return {"content": "\n\n".join(content)}