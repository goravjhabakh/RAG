
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import UploadFile, File
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    user_id: str = Field(..., description="User id")
    user_role: str = Field(..., description="User role")
    access_roles: List[str] = Field(
        default_factory=list,
        description="Access roles"
    )
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "project-specs.pdf",
                "user_id": "usr-12345",
                "user_role": "project-manager",
                "access_roles": ["qa-team", "devops"],
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        }

class DocumentProcessingResponse(BaseModel):
    """Response model for document processing"""
    document_id: str
    status: DocumentStatus
    message: str
    filename: str
    chunks_created: Optional[int] = None
    processing_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QueryRequest(BaseModel):
    """Request model for querying documents"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    user_id: str = Field(..., description="User making the query")
    user_role: str = Field(..., description="User's role for access control")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BaseResponse(BaseModel):
    """Base response model"""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentResponse(BaseResponse):
    """Document operation response"""
    data: Optional[DocumentProcessingResponse] = None