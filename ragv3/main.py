from fastapi import FastAPI
from api.routes import router
from logs.main import LOGGER

logger = LOGGER.get_logger()

def create_app() -> FastAPI:
    logger.info('Starting backend...')
    app = FastAPI(title='Book Management System')

    logger.info('Setting up routing...')
    app.include_router(router)
    return app

app = create_app()