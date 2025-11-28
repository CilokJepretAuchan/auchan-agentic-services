from core.supabase import supabase

from core.memory import job_statuses
from core.models import JobStatus
from services.data_aggregator import get_monthly_financial_context
from core.models import FinancialContext
from services.runner.report_builder_runner import BuildReportCrewRunner
from template.generator import generate_monthly_report_pdf

def report_builder_background(job_id: str, org_id: str, month: int, year: int):
    """
    This function runs in the background to build a report.
    It updates the job status in the in-memory store.
    """
    # 1. Get the job object from the in-memory store
    job = job_statuses.get(job_id)
    if not job:
        # This should not happen if the job was created correctly
        print(f"Error: Job with ID {job_id} not found.")
        return

    try:

        Aggregated_data : FinancialContext = get_monthly_financial_context(org_id=org_id, month=month, year=year)
        
        report = BuildReportCrewRunner.run_extraction(aggregated_data=Aggregated_data.model_dump_json())

        output_path,unique_filename = generate_monthly_report_pdf(report)


        job.status = JobStatus.COMPLETED
        job.result = {
            "time-period": f"{month:02d}-{year}",
            "org": org_id,
            "num aggregated data": len(Aggregated_data.projects),
            "report_file": unique_filename,
            "report_path": output_path
        }


    except Exception as e:
        # If any step fails, update job status to FAILED
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        print(f"Error processing job {job_id}: {e}")

    finally:
        # 5. Always update the timestamp
        job.touch()

