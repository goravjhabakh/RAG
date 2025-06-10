# from fastapi import FastAPI
# from api.routes import router

# def create_app() -> FastAPI:
#     app = FastAPI(title = 'RAG')
#     app.include_router(router=router)
#     return app

# app = create_app()

import asyncio
from services.processor import DocumentProcessor

if __name__ == "__main__":
    processor = DocumentProcessor(
        mongodb_uri='mongodb+srv://goravjhabakh1301:rarr9Zkq42OJ5csB@rag.1vunq22.mongodb.net/',
        db_name='rag_db',
        collection_name='documents',
        vector_index_name='vindex'
    )

    asyncio.run(processor.process_document(
        file_path='files/RAG Paper.pdf'
    ))
