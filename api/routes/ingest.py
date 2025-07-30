from fastapi import APIRouter, UploadFile
from ingestion.pdf_extractor import extract_text_from_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile):
    content = extract_text_from_pdf(file.file)
    return {"text": content}