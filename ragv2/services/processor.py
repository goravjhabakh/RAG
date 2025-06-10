
import os
import uuid
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from pymongo import MongoClient
import google.generativeai as genai
from models.model import DocumentStatus, DocumentProcessingResponse
from logs.logging import LOGGER
from langchain_huggingface import HuggingFaceEmbeddings

logger = LOGGER.get_logger()

class DocumentProcessor:
    def __init__(
        self, 
        mongodb_uri: str,
        db_name: str = "rag_db",
        collection_name: str = "documents",
        vector_index_name: str = "vector_index"
    ):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.vector_index_name = vector_index_name
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
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

    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        try:
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            unique_filename = f"{file_id}_{filename}"
            file_path = self.upload_dir / unique_filename

            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"File saved successfully: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise

    def partition_document(self, file_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Partitioning document: {file_path}")

            elements = partition(
                filename=file_path,
                infer_table_structure=False,
                include_page_breaks=True,
                extract_images=False
            )

            full_text = ""
            text_page_numbers = set()
            tables = []

            for element in elements:
                text = str(element).strip()
                page_number = getattr(element.metadata, "page_number", None)

                # Skip empty content
                if not text:
                    continue

                if element.category == "Table":
                    # Save each table with its page number
                    tables.append({
                        "page_number": page_number,
                        "text": text,
                        "metadata": element.metadata.to_dict()
                    })
                else:
                    # Accumulate text and page numbers for later chunking
                    full_text += text + "\n\n"
                    if page_number is not None:
                        text_page_numbers.add(page_number)

            logger.info(f"Collected {len(tables)} tables and text from {len(text_page_numbers)} pages")

            return {
                "combined_text": full_text.strip(),
                "text_pages": sorted(text_page_numbers),
                "tables": tables
            }

        except Exception as e:
            logger.error(f"Error partitioning document {file_path}: {str(e)}")
            raise

    def chunk_elements(
        self, 
        partitioned: Dict[str, Any],
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[Document]:
        try:
            logger.info(f"Chunking combined text with size={chunk_size}, overlap={chunk_overlap}")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            documents = []

            # Split the combined text into chunks
            chunks = text_splitter.split_text(partitioned["combined_text"])
            pages = partitioned["text_pages"]

            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "chunk_id": i,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "page_numbers": pages
                    }
                ))

            # Also add the tables as documents (if needed)
            for table in partitioned["tables"]:
                documents.append(Document(
                    page_content=table["text"],
                    metadata={
                        "type": "table",
                        "page_number": table["page_number"],
                        **table["metadata"]
                    }
                ))

            logger.info(f"Created {len(documents)} document entries (text + tables)")
            return documents

        except Exception as e:
            logger.error(f"Error chunking elements: {str(e)}")
            raise

    def store_documents(
        self, 
        documents: List[Document], 
        document_metadata: Dict[str, Any]
    ) -> int:
        try:
            logger.info(f"Storing {len(documents)} documents in vector store")

            for doc in documents:
                doc.metadata.update(document_metadata)

            doc_ids = o.to_thread(
                self.vector_store.add_documents, 
                documents
            )

            logger.info(f"Successfully stored {len(doc_ids)} documents")
            return len(doc_ids)

        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise

    def create_search_index(self) -> Dict[str, Any]:
        try:
            index_definition = {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 384, 
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

            logger.info("Vector search index definition created")
            return index_definition

        except Exception as e:
            logger.error(f"Error creating search index: {str(e)}")
            raise

    def process_document(
        self,
        file_path: str,
        filename: str = 'FILENAME',
        user_id: str = '1',
        user_role: str = 'ADMIN',
        access_roles: List[str] = ['ADMIN','USER'],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> DocumentProcessingResponse:
        start_time = datetime.utcnow()
        document_id = str(uuid.uuid4())

        try:
            logger.info(f"Starting document processing for {filename}")

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
            chunks_created = self.store_documents(documents, document_metadata)

            # Calculate processing time
            processing_time = (datetime.utcnow - start_time).total_seconds()

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
        
