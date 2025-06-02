from pydantic import BaseModel
from typing import Optional, Any

# Main model for books
class Book(BaseModel):
    id: int
    name: str
    author: str

# Model to update books as it has Optional for flexibility
class BookUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None

# Model for API response
class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None