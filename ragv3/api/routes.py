from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse
from typing import List
import os
from services.doc_processor import process_document
from services.query import handle_query
from logs.main import LOGGER

logger = LOGGER.get_logger()
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_files(files: List[UploadFile]):
    results = []

    for file in files:
        file_path = os.path.join(FILES_DIR, file.filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            response = process_document(file_path, filename=file.filename)
            results.append(response)
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })

    return JSONResponse(content={
        "message": f"Processed {len(results)} file(s)",
        "results": results
    })

@router.post("/query", status_code=status.HTTP_200_OK)
async def process_query(query: str):
    try:
        answer = await handle_query(query)
        logger.info("Query processed successfully")
        return {
            "success": True,
            "query": query,
            "answer": answer['result']
        }
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return {
            'sucess': False,
            'error': str(e)
        }