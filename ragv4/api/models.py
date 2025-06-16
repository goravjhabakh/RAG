from pydantic import BaseModel, Field
from typing import List, Optional

class StoreRequest(BaseModel):
    user_id: int
    access_roles: Optional[List] = Field(default=None)

class UploadResponse(BaseModel):
    success: bool
    message:str = ''
    uploaded_files: List[str] = []
    total_chunks: int = 0

class QueryRequest(BaseModel):
    query: str
    user_id: int