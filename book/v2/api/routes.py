from models.book import Book, BookUpdate, APIResponse
from repository import repo
from fastapi import APIRouter
from logs.logging import LOGGER

logger = LOGGER.get_logger()
router = APIRouter(prefix='/books', tags=['Books'])

@router.post("/create", response_model=APIResponse)
def create_book(book: Book):
    logger.info(f"POST /create - Received book with ID: {book.id}")
    existing = repo.get_book(book.id)
    if existing:
        logger.warning(f"Book with ID {book.id} already exists.")
        return APIResponse(success=False, message="Book already exists.")
    inserted_id = repo.create_book(book.model_dump())
    logger.info(f"Book created with Mongo ID: {inserted_id}")
    return APIResponse(success=True, message="Book created", data={"inserted_id": str(inserted_id)})

@router.get("/read/{book_id}", response_model=APIResponse)
def read_book(book_id: int):
    logger.info(f"GET /read/{book_id} - Fetching book")
    book = repo.get_book(book_id)
    if not book:
        logger.warning(f"Book with ID {book_id} not found.")
        return APIResponse(success=False, message="Book not found")

    book = book.copy()
    if '_id' in book:
        book['_id'] = str(book['_id'])
    logger.info(f"Book with ID {book_id} retrieved.")
    return APIResponse(success=True, message="Book found", data=book)

@router.get("/read-all", response_model=APIResponse)
def read_all_books():
    logger.info("GET /read-all - Retrieving all books")
    books = repo.get_all_books()
    books = [book.copy() for book in books]
    for book in books:
        if '_id' in book:
            book['_id'] = str(book['_id'])
    logger.info(f"{len(books)} books retrieved.")
    return APIResponse(success=True, message="Books retrieved", data=books)

@router.put("/update/{book_id}", response_model=APIResponse)
def update_book(book_id: int, book: BookUpdate):
    logger.info(f"PUT /update/{book_id} - Updating book with data: {book.model_dump(exclude_unset=True)}")
    success = repo.update_book(book_id, book.model_dump(exclude_unset=True))
    if not success:
        logger.warning(f"Book with ID {book_id} not found for update.")
        return APIResponse(success=False, message="Book not found")
    logger.info(f"Book with ID {book_id} successfully updated.")
    return APIResponse(success=True, message="Book updated")

@router.patch("/update/{book_id}", response_model=APIResponse)
def patch_book(book_id: int, book: BookUpdate):
    logger.info(f"PATCH /update/{book_id} - Partially updating book with data: {book.model_dump(exclude_unset=True)}")
    success = repo.patch_book(book_id, book.model_dump(exclude_unset=True))
    if not success:
        logger.warning(f"Book with ID {book_id} not found for patch.")
        return APIResponse(success=False, message="Book not found")
    logger.info(f"Book with ID {book_id} partially updated.")
    return APIResponse(success=True, message="Book partially updated")

@router.delete("/delete/{book_id}", response_model=APIResponse)
def delete_book(book_id: int):
    logger.info(f"DELETE /delete/{book_id} - Deleting book")
    success = repo.delete_book(book_id)
    if not success:
        logger.warning(f"Book with ID {book_id} not found for deletion.")
        return APIResponse(success=False, message="Book not found")
    logger.info(f"Book with ID {book_id} deleted successfully.")
    return APIResponse(success=True, message="Book deleted")