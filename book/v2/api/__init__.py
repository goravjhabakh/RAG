from fastapi import FastAPI
from api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(title='Book Management System')
    app.include_router(router)
    return app