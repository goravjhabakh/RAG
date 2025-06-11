from fastapi import APIRouter, UploadFile, File, status, Form
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from api.models import StoreRequest, UploadResponse
from typing import List
from datetime import datetime
import os
from services.utility import store_documents, process_document
from services.indexing import update_search_index
from services.query import handle_query
from services.log import LOGGER
from services.history import load_chat_history, save_chat_history

router = APIRouter(prefix='/rag')
local_fil_dir = 'files'
os.makedirs(local_fil_dir, exist_ok=True)
logger = LOGGER.get_logger()

@router.post('/upload')
async def upload_document(documents: List[UploadFile] = File(...), other_data: str = Form(...)):
    try:
        data = StoreRequest.model_validate_json(other_data)
        paths = await store_documents(documents, local_fil_dir)

        for path in paths:
            total_chunks = await process_document(path, data.access_roles)
        
        await update_search_index()
        return UploadResponse(
            success=True,
            message='Uploaded all documents and updated search index',
            uploaded_files = [doc.filename for doc in documents],
            total_chunks = total_chunks
        )


    except Exception as e:
        return JSONResponse(
            status_code=500,
            content = {'error': str(e)}
        )
    
@router.post("/query", status_code=status.HTTP_200_OK)
async def process_query(query: str, user_id: int):
    try:
        query_time = datetime.now()
        answer = await handle_query(query)
        answer_time = datetime.now()
        logger.info("Query processed successfully")

        await save_chat_history(user_id, query, answer['result'], query_time, answer_time)

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
    
@router.get('/load-chat-history/{user_id}', status_code=status.HTTP_200_OK)
async def load_history(user_id: int):
    try:
        history = await load_chat_history(user_id)
        return {
            'success': True,
            'history': history
        }

    except Exception as e:
        logger.error(f"Loading chat history failed: {str(e)}")
        return {
            'sucess': False,
            'error': str(e)
        }