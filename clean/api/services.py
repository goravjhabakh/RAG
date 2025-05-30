import os
import shutil
from fastapi import UploadFile
from converters.pdf import PDFToMarkdownConverter

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_file_upload(file: UploadFile) -> dict:
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    converter = PDFToMarkdownConverter(pdf_dir=UPLOAD_DIR, md_dir="not_needed")
    result = converter._convert_single_pdf(file_path)

    return result  