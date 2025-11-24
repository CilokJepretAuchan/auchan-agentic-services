from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool # <--- Import penting
import tempfile
import shutil
import os
from services.Extractor_crew_runner import ExtractorCrewRunner
from utils.custom_tools.docx_tool import DocxReaderTool
from utils.utils import map_transactions
from core.supabase import supabase

router = APIRouter()

@router.post("/extract/docx")
async def extract_from_docx(userId:str,orgId:str,projectId:str,file: UploadFile = File(...)):
    # 1. Validasi tipe file
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="File must be a .docx document")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        
        docx_tool = DocxReaderTool()
        try:
            parsed_document = await run_in_threadpool(docx_tool._run, temp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

        try:
            result = await run_in_threadpool(ExtractorCrewRunner.run_extraction, parsed_document)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Crew processing failed: {str(e)}")
        

        mapped_transactions = map_transactions(
            extracted_doc=result,
            user_id=userId,
            org_id=orgId,
            project_id=projectId
        )
        
        try:
            response = supabase.table("Transaction").insert(mapped_transactions).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(e)}")
        

        return {
    "status": "success",
    "response" : response
}


    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)