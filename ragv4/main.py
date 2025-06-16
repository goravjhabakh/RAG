from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app

app = create_app()