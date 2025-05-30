from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from api.services import handle_file_upload
import os

router = APIRouter()

@router.post("")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported"})

    output = await handle_file_upload(file)
    return {"result": output}