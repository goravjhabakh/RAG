from fastapi import FastAPI
from api.routes import router
from logs.logging import LOGGER
from api.exceptions import BookNotFoundException, BookAlreadyExistsException, NoBooksFoundException
from api.exception_handler import book_exists_handler, book_not_found_handler, no_books_handler

logger = LOGGER.get_logger()

def create_app() -> FastAPI:
    logger.info('Starting backend...')
    app = FastAPI(title='Book Management System')

    logger.info('Setting up routing...')
    app.include_router(router)
    return app

app = create_app()
app.add_exception_handler(BookNotFoundException, book_not_found_handler)
app.add_exception_handler(BookAlreadyExistsException, book_exists_handler)
app.add_exception_handler(NoBooksFoundException, no_books_handler)