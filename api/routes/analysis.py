import uuid
from fastapi import APIRouter, BackgroundTasks

# Local imports
from core.memory import job_statuses
from core.models import Job
from services.runner.anomaly_runner_bg import run_anomaly_pipeline_background

# --- Router Setup ---
router = APIRouter()

# --- Endpoints ---

@router.post("/analysis/run-anomaly-detection", response_model=Job, status_code=202)
async def run_analysis(
    background_tasks: BackgroundTasks,
):
    """
    Triggers the anomaly detection pipeline to run in the background.
    
    This endpoint processes all data in the database, so it doesn't require
    specific user/project context in the request itself.
    """
    # 1. Create a unique job for this analysis run
    job_id = str(uuid.uuid4())
    
    # Create a job with placeholder IDs, as this is a system-wide task.
    # In a real multi-tenant app, this might come from an admin user's context.
    new_job = Job(
        job_id=job_id,
        project_id="GLOBAL_ANALYSIS",
        user_id="SYSTEM",
        org_id="SYSTEM"
    )
    job_statuses[job_id] = new_job

    # 2. Add the pipeline function to the background queue
    background_tasks.add_task(
        run_anomaly_pipeline_background, 
        job_id=job_id
    )

    # 3. Return the accepted job object immediately
    return new_job
