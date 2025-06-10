from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status
from models.book import APIResponse
from api.exceptions import BookNotFoundException, BookAlreadyExistsException, NoBooksFoundException

async def book_not_found_handler(request: Request, exc: BookNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=APIResponse(success=False, error=exc.msg).model_dump()
    )

async def book_exists_handler(request: Request, exc: BookAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=APIResponse(success=False, error=exc.msg).model_dump()
    )

async def no_books_handler(request: Request, exc: NoBooksFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=APIResponse(success=False, error=exc.msg).model_dump()
    )