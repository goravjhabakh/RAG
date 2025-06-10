from fastapi import APIRouter, UploadFile, File, status
from typing import List
import os
from services.extract import extract_document

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)
router = APIRouter(prefix='/rag', tags=['RAG'])

@router.post('/upload', status_code=status.HTTP_200_OK)
async def upload_files(files: List[UploadFile]):
    
    saved_files = []

    for file in files:
        file_loc = os.path.join(FILES_DIR, file.filename)

        with open(file_loc, 'wb') as f:
            content = await file.read()
            f.write(content)

        saved_files.append(file_loc)

        try:
            elements = extract_document(file_loc)
            # print(elements['text'])
            # print(elements['tables'])

        except Exception as e:
            print(e)
    
    return {
        'success': True,
        'message': f'Saved {len(saved_files)}files',
        'files': saved_files
    }