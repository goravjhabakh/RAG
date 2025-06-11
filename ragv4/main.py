from fastapi import FastAPI
from api.routes import router

def create_app():
    app = FastAPI()
    app.include_router(router)
    return app

app = create_app()