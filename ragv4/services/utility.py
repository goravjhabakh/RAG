from fastapi import UploadFile
from typing import List
import os 
from services.log import LOGGER
from unstructured.partition.auto import partition
from services.mongo import MongoDBClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from sentence_transformers import CrossEncoder
from pydantic import Field

logger = LOGGER.get_logger()

async def store_documents(documents: List[UploadFile], path: str) -> List[str]:
    logger.info(f'Saving {len(documents)} document(s) locally')

    paths = []
    for doc in documents:
        stored_file_path = os.path.join(path, doc.filename)

        with open(stored_file_path, "wb") as f:
            content = await doc.read()
            f.write(content)
        
        logger.info(f'Saved {stored_file_path}')
        paths.append(stored_file_path)

    return paths

def partition_document(file_path: str) -> str:
    try:
        logger.info(f"Partitioning document: {file_path}")

        elements = partition(
            filename=file_path,
            infer_table_structure=True,
            include_page_breaks=True,
            extract_images=False
        )

        full_text_parts = []

        for element in elements:
            text = str(element)
            if text:
                full_text_parts.append(text)

        return "\n\n".join(full_text_parts)

    except Exception as e:
        logger.error(f"Error partitioning document {file_path}: {str(e)}")
        raise

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

class EmbeddingStore:
    def __init__(self, db_name = 'documents', collection = 'collection1', index_name = 'vindex'):
        self.client = MongoDBClient.get_client()
        self.db = self.client[db_name]
        self.collection = self.db[collection]
        self.index_name = index_name
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = MongoDBAtlasVectorSearch(
            collection = self.collection,
            embedding = self.embeddings,
            index_name = self.index_name,
            text_key = 'text',
            embedding_key = 'embedding'
        )
    
    def add_documents(self, docs: List[Document], access_roles: List[str]):
        try:
            logger.info(f"Embedding and storing {len(docs)} documents")
            documents = [Document(page_content=doc.page_content, metadata={'access_roles': access_roles, 'chunk_index': i, **doc.metadata}) for i, doc in enumerate(docs)]

            self.vector_store.add_documents(documents)
            logger.info("Successfully stored documents with embeddings")

        except Exception as e:
            logger.error(f"Failed to embed/store documents: {str(e)}")
            raise


async def process_document(path: str, access_roles: List[str]):
    try:
        logger.info(f"Starting full document processing for: {path}")

        full_text = partition_document(path)
        chunks = chunk_text(full_text)
        store = EmbeddingStore(collection='test').add_documents(chunks, access_roles)

        logger.info(f"Document processing complete: {len(chunks)} chunks stored.")
        return (len(chunks))

    except Exception as e:
        logger.error(f"Error during document processing: {str(e)}")

class RerankRetriever(BaseRetriever):
    retriever: BaseRetriever = Field(...)
    reranker: CrossEncoder = Field(...)
    top_k: int = 3

    def _get_relevant_documents(self, query: str) -> List[Document]:
        initial_docs = self.retriever.invoke(query)
        pairs = [(query, doc.page_content) for doc in initial_docs]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(scores, initial_docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in reranked[:self.top_k]]