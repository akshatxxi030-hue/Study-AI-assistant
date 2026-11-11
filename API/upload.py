from fastapi import APIRouter, UploadFile, File
import shutil
import os
from INGESTIONS.loader import pdf_loader
from INGESTIONS.splitter import split_text
from INGESTIONS.embeddings import get_embeddings
from INGESTIONS.vector_store import store_embeddings

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    docs=pdf_loader(temp_path)
    chunks=split_text(docs)
    embeddings=get_embeddings()
    store_embeddings(chunks)

    os.remove(temp_path)

    return {"filename": file.filename, "status": "uploaded"}