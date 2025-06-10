
import os
import uuid
import tempfile
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

# Document processing imports
from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from pymongo import MongoClient
import google.generativeai as genai
from models.model import DocumentStatus, DocumentProcessingResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiEmbeddings:
    """Custom Gemini embeddings class for LangChain compatibility"""

    def __init__(self, api_key: str, model_name: str = "text-embedding-004"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']

class DocumentProcessor:
    """Main document processing service"""

    def __init__(
        self, 
        mongodb_uri: str,
        gemini_api_key: str,
        db_name: str = "rag_db",
        collection_name: str = "documents",
        vector_index_name: str = "vector_index"
    ):
        self.mongodb_uri = mongodb_uri
        self.gemini_api_key = gemini_api_key
        self.db_name = db_name
        self.collection_name = collection_name
        self.vector_index_name = vector_index_name

        # Initialize MongoDB client
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # Initialize embeddings
        self.embeddings = GeminiEmbeddings(gemini_api_key)

        # Initialize vector store
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name=vector_index_name,
            text_key="text",
            embedding_key="embedding"
        )

        # Create upload directory
        self.upload_dir = Path("files")
        self.upload_dir.mkdir(exist_ok=True)

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to local storage"""
        try:
            # Generate unique filename to prevent conflicts
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            unique_filename = f"{file_id}_{filename}"
            file_path = self.upload_dir / unique_filename

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"File saved successfully: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise

    def partition_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Use Unstructured to partition document into elements"""
        try:
            logger.info(f"Partitioning document: {file_path}")

            # Partition document with table extraction
            elements = partition(
                filename=file_path,
                strategy="hi_res",  # Use hi_res for table extraction
                infer_table_structure=True,  # Extract table structure
                include_page_breaks=True,
                extract_images=False  # Set to True if you want image extraction
            )

            # Convert elements to dictionaries with metadata
            processed_elements = []
            for element in elements:
                element_dict = {
                    "type": element.category if hasattr(element, 'category') else 'Unknown',
                    "text": str(element),
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }

                # Add HTML table structure if available
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'text_as_html'):
                    element_dict["metadata"]["html_content"] = element.metadata.text_as_html

                processed_elements.append(element_dict)

            logger.info(f"Document partitioned into {len(processed_elements)} elements")
            return processed_elements

        except Exception as e:
            logger.error(f"Error partitioning document {file_path}: {str(e)}")
            raise

    def chunk_elements(
        self, 
        elements: List[Dict[str, Any]], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[Document]:
        """Chunk elements using LangChain text splitter"""
        try:
            logger.info(f"Chunking elements with size={chunk_size}, overlap={chunk_overlap}")

            # Initialize text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            documents = []

            for i, element in enumerate(elements):
                # Create base metadata
                metadata = {
                    "element_id": i,
                    "element_type": element["type"],
                    **element["metadata"]
                }

                # Split text into chunks
                if element["text"].strip():  # Only process non-empty text
                    chunks = text_splitter.split_text(element["text"])

                    for j, chunk in enumerate(chunks):
                        chunk_metadata = {
                            **metadata,
                            "chunk_id": f"{i}_{j}",
                            "chunk_index": j,
                            "total_chunks": len(chunks)
                        }

                        documents.append(Document(
                            page_content=chunk,
                            metadata=chunk_metadata
                        ))

            logger.info(f"Created {len(documents)} document chunks")
            return documents

        except Exception as e:
            logger.error(f"Error chunking elements: {str(e)}")
            raise

    async def store_documents(
        self, 
        documents: List[Document], 
        document_metadata: Dict[str, Any]
    ) -> int:
        """Store documents in MongoDB Atlas with vector embeddings"""
        try:
            logger.info(f"Storing {len(documents)} documents in vector store")

            # Add document-level metadata to each chunk
            for doc in documents:
                doc.metadata.update(document_metadata)

            # Store documents in vector store (this handles embedding generation)
            doc_ids = await asyncio.to_thread(
                self.vector_store.add_documents, 
                documents
            )

            logger.info(f"Successfully stored {len(doc_ids)} documents")
            return len(doc_ids)

        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise

    def create_search_index(self) -> Dict[str, Any]:
        """Create MongoDB Atlas Vector Search index"""
        try:
            # Vector search index definition
            index_definition = {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 768,  # Gemini text-embedding-004 dimensions
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "metadata.user_id"
                    },
                    {
                        "type": "filter", 
                        "path": "metadata.access_roles"
                    },
                    {
                        "type": "filter",
                        "path": "metadata.element_type"
                    }
                ]
            }

            # Note: In practice, you would create this index through MongoDB Atlas UI
            # or using the Atlas Admin API. This is a placeholder for the index structure.
            logger.info("Vector search index definition created")
            return index_definition

        except Exception as e:
            logger.error(f"Error creating search index: {str(e)}")
            raise

    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        user_role: str,
        access_roles: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> DocumentProcessingResponse:
        """Complete document processing pipeline"""
        start_time = datetime.utcnow()
        document_id = str(uuid.uuid4())

        try:
            logger.info(f"Starting document processing for {filename}")

            # Step 1: Save file locally
            file_path = await self.save_uploaded_file(file_content, filename)

            # Step 2: Partition document using Unstructured
            elements = self.partition_document(file_path)

            # Step 3: Chunk elements
            documents = self.chunk_elements(elements, chunk_size, chunk_overlap)

            # Step 4: Prepare document metadata
            document_metadata = {
                "document_id": document_id,
                "filename": filename,
                "user_id": user_id,
                "user_role": user_role,
                "access_roles": access_roles,
                "upload_timestamp": start_time.isoformat(),
                "file_path": file_path
            }

            # Step 5: Store documents with embeddings
            chunks_created = await self.store_documents(documents, document_metadata)

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Clean up temporary file (optional)
            # os.remove(file_path)

            logger.info(f"Document processing completed successfully for {filename}")

            return DocumentProcessingResponse(
                document_id=document_id,
                status=DocumentStatus.COMPLETED,
                message="Document processed and stored successfully",
                filename=filename,
                chunks_created=chunks_created,
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            return DocumentProcessingResponse(
                document_id=document_id,
                status=DocumentStatus.FAILED,
                message=f"Document processing failed: {str(e)}",
                filename=filename
            )

# Usage example and configuration
class DocumentProcessorConfig:
    """Configuration class for document processor"""

    def __init__(self):
        # Environment variables (set these in your .env file)
        self.MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://username:password@cluster.mongodb.net/")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
        self.DB_NAME = os.getenv("DB_NAME", "rag_db")
        self.COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
        self.VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "vector_index")

    def create_processor(self) -> DocumentProcessor:
        """Create and return a configured document processor"""
        return DocumentProcessor(
            mongodb_uri=self.MONGODB_URI,
            gemini_api_key=self.GEMINI_API_KEY,
            db_name=self.DB_NAME,
            collection_name=self.COLLECTION_NAME,
            vector_index_name=self.VECTOR_INDEX_NAME
        )
