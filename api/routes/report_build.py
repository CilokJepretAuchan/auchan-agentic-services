
import os
from fastapi import HTTPException
import uuid
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from services.background.report_builder_bg import report_builder_background
from utils.utils import validate_month_year_exists
from core.memory import job_statuses

from core.models import BuildReportRequest, Job, JobStatus
router = APIRouter()
@router.post("/build-report", response_model=Job, status_code=200)
async def build_report(
    req: BuildReportRequest,
    background_tasks: BackgroundTasks,
):
    """
    Endpoint to initiate the report building process for a given organization and time period.
    Accepts body request JSON.
    """
    is_valid = validate_month_year_exists(month=req.month, year=req.year)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="No transactions found for the specified month and year."
        )
    
    job_id = str(uuid.uuid4())
    new_job = Job(
        job_id=job_id,
        org_id=req.org_id
    )
    
    job_statuses[job_id] = new_job

    # Queue the background task
    background_tasks.add_task(
        report_builder_background,
        job_id=job_id,
        org_id=req.org_id,
        month=req.month,
        year=req.year
    )

    return new_job


@router.get("/build-report/status/{job_id}", response_model=Job)
async def get_extract_status(job_id: str):
    """
    Retrieves the current status of a background processing job.
    """
    job = job_statuses.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/extract/download/{job_id}")
async def download_extracted_file(job_id: str):
    """
    Endpoint to download the extracted file once processing is complete.
    """
    job = job_statuses.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not yet completed")

    # Assuming the extracted file path is stored in the job object
    extracted_file_path = job.result.get("report_path")
    if not os.path.exists(extracted_file_path):
        raise HTTPException(status_code=500, detail="Extracted file not found")

    return FileResponse(extracted_file_path, media_type='application/octet-stream', filename=os.path.basename(extracted_file_path))

