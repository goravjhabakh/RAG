from store.partioner import partition_document
from store.chunking import chunk_text
from store.embedding import EmbeddingStore
from logs.main import LOGGER
from langchain_core.documents import Document
from typing import Dict, Any

logger = LOGGER.get_logger()

def process_document(file_path: str, filename: str = "uploaded_file.pdf") -> Dict[str, Any]:
    try:
        logger.info(f"Starting full document processing for: {file_path}")

        full_text = partition_document(file_path)
        chunks = chunk_text(full_text)
        store = EmbeddingStore().add_documents(chunks)

        logger.info(f"Document processing complete: {len(chunks)} chunks stored.")

        return {
            "success": True,
            "filename": filename,
            "chunks_created": len(chunks)
        }

    except Exception as e:
        logger.error(f"Error during document processing: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }