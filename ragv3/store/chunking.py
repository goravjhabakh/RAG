from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from logs.main import LOGGER

logger = LOGGER.get_logger()

def chunk_text(full_text: str, chunk_size: int = 1200, chunk_overlap: int = 300) -> List[Document]:
    try:
        logger.info(f"Chunking text: size={chunk_size}, overlap={chunk_overlap}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_text(full_text)
        logger.info(f"Text split into {len(chunks)} chunks")

        documents = [
            Document(page_content=chunk, metadata={"chunk_index": i})
            for i, chunk in enumerate(chunks)
        ]

        return documents

    except Exception as e:
        logger.error(f"Error while chunking text: {str(e)}")
        raise