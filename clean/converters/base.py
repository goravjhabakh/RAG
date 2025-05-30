from typing import Dict

class BaseDocumentConverter:
    def convert(self, file_path: str) -> Dict[str, str]:
        raise NotImplementedError