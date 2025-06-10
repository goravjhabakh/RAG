from models.book import Book, BookUpdate, APIResponse
from repository import repo
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from logs.logging import LOGGER
from api.exceptions import BookAlreadyExistsException, BookNotFoundException, NoBooksFoundException

logger = LOGGER.get_logger()
router = APIRouter(prefix='/books', tags=['Books'])

@router.post("/create", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    logger.info(f"POST /create - Received book with ID: {book.id}")
    existing = await repo.get_book(book.id)
    if existing:
        logger.warning(f"Book with ID {book.id} already exists.")
        # return JSONResponse(
        #     status_code=status.HTTP_409_CONFLICT,
        #     content=APIResponse(success=False, message="Book already exists.").model_dump()
        # )
        raise BookAlreadyExistsException(book.id)
    inserted_id = await repo.create_book(book.model_dump())
    logger.info(f"Book created with Mongo ID: {inserted_id}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book created", data={"inserted_id": str(inserted_id)}).model_dump()
    )

@router.get("/read/{book_id}", response_model=APIResponse)
async def read_book(book_id: int):
    logger.info(f"GET /read/{book_id} - Fetching book")
    book = await repo.get_book(book_id)
    if not book:
        logger.warning(f"Book with ID {book_id} not found.")
        # return JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content=APIResponse(success=False, message="Book not found").model_dump()
        # ) # model_dump() converts pydantic model to normal dictionary
        raise BookNotFoundException(book_id)

    if '_id' in book:
        book['_id'] = str(book['_id'])
    logger.info(f"Book with ID {book_id} retrieved.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book found", data=book).model_dump()
    )

@router.get("/read-all", response_model=APIResponse)
async def read_all_books():
    logger.info("GET /read-all - Retrieving all books")
    books = await repo.get_all_books()
    if len(books) == 0:
        logger.warning(f"Books not found")
        # return JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content=APIResponse(success=False, message="Books not found").model_dump()
        # )
        raise NoBooksFoundException()

    for book in books:
        if '_id' in book:
            book['_id'] = str(book['_id'])
    logger.info(f"{len(books)} books retrieved.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book found", data=books).model_dump()
    )

@router.put("/update/{book_id}", response_model=APIResponse)
async def update_book(book_id: int, book: BookUpdate):
    logger.info(f"PUT /update/{book_id} - Updating book with data: {book.model_dump(exclude_unset=True)}")
    success = await repo.update_book(book_id, book.model_dump(exclude_unset=True))
    if not success:
        logger.warning(f"Book with ID {book_id} not found for update.")
        # return JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content=APIResponse(success=False, message="Book not found").model_dump()
        # )
        raise BookNotFoundException(book_id)
    logger.info(f"Book with ID {book_id} successfully updated.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book updated").model_dump()
    )

@router.patch("/update/{book_id}", response_model=APIResponse)
async def patch_book(book_id: int, book: BookUpdate):
    logger.info(f"PATCH /update/{book_id} - Partially updating book with data: {book.model_dump(exclude_unset=True)}")
    success = await repo.patch_book(book_id, book.model_dump(exclude_unset=True))
    if not success:
        logger.warning(f"Book with ID {book_id} not found for patch.")
        # return JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content=APIResponse(success=False, message="Book not found").model_dump()
        # )
        raise BookNotFoundException(book_id)
    logger.info(f"Book with ID {book_id} partially updated.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book partially updated").model_dump()
    )

@router.delete("/delete/{book_id}", response_model=APIResponse)
async def delete_book(book_id: int):
    logger.info(f"DELETE /delete/{book_id} - Deleting book")
    success = await repo.delete_book(book_id)
    if not success:
        logger.warning(f"Book with ID {book_id} not found for deletion.")
        # return JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content=APIResponse(success=False, message="Book not found").model_dump()
        # )
        raise BookNotFoundException(book_id)
    logger.info(f"Book with ID {book_id} deleted successfully.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(success=True, message="Book deleted").model_dump()
    )