from typing import List
from services.mongo import MongoDBClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from logs.main import LOGGER

logger = LOGGER.get_logger()

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
    
    def add_documents(self, docs: List[Document]):
        try:
            logger.info(f"Embedding and storing {len(docs)} documents")
            self.vector_store.add_documents(docs)
            logger.info("Successfully stored documents with embeddings")

        except Exception as e:
            logger.error(f"Failed to embed/store documents: {str(e)}")
            raise