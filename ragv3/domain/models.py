from pydantic import BaseModel, Field
from typing import Optional, List

class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., description="File name")
    file_path: str = Field(..., description="File Path")
    chunk_size: Optional[int] = Field(default=1000, le=4000, ge=100, description="Chunk size for text splitting")
    chunk_overlap: Optional[int] = Field(default=200, le=500, ge=0, description="Chunk overlap for text splitting")