import uuid
import shutil
import os
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# Local imports
from core.memory import job_statuses
from core.models import Job, JobStatus
from services.background.extract_file_bg import process_document_background

# --- Router Setup ---
router = APIRouter()
load_dotenv()
TEMP_UPLOAD_DIR = os.getenv("TEMP_UPLOAD_DIR")

# --- Endpoints ---

@router.post("/extract/docx", response_model=Job, status_code=202)
async def extract_from_docx(
    userId: str,
    orgId: str,
    projectId: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Accepts a .docx file, saves it temporarily, and queues it for background processing.
    Returns a job object immediately, which can be used to track the status.
    """
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="File must be a .docx document")

    # 1. Create a unique job and store its initial state
    job_id = str(uuid.uuid4())
    new_job = Job(
        job_id=job_id,
        project_id=projectId,
        user_id=userId,
        org_id=orgId
    )
    job_statuses[job_id] = new_job

    # 2. Save the uploaded file to a temporary location for the background worker
    try:
        file_extension = file.filename.split(".")[-1]
        # We can use the job_id to name the file for easy tracking
        unique_filename = f"{job_id}.{file_extension}"
        file_path = os.path.join(TEMP_UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        # If saving fails, update the job status to 'failed'
        new_job.status = JobStatus.FAILED
        new_job.error_message = f"Failed to save temporary file: {str(e)}"
        new_job.touch()
        raise HTTPException(status_code=500, detail=new_job.error_message)

    # 3. Add the processing task to the background queue
    # The background task only needs the job_id to find all other info
    background_tasks.add_task(
        process_document_background, 
        job_id=job_id, 
        file_path=file_path
    )

    # 4. Return the accepted job object immediately
    return new_job


@router.get("/extract/status/{job_id}", response_model=Job)
async def get_extract_status(job_id: str):
    """
    Retrieves the current status of a background processing job.
    """
    job = job_statuses.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


