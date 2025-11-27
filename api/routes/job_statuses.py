from fastapi import APIRouter
from app import job_extract_statuses

router = APIRouter()

@router.get("/job_status/{job_id}")
async def get_job_status(job_id: str):
    """
    Endpoint untuk mendapatkan status job ekstraksi berdasarkan job_id.
    """
    status_info = job_extract_statuses.get(job_id)
    if not status_info:
        return {"error": "Job ID tidak ditemukan"}
    return {"job_id": job_id, "status": status_info["status"], "message": status_info["message"]}