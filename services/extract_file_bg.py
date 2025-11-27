import os
from services.Extractor_crew_runner import ExtractorCrewRunner
from utils.custom_tools.docx_tool import DocxReaderTool
from utils.utils import map_transactions
from core.supabase import supabase

# Local imports for status tracking
from core.memory import job_statuses
from core.models import JobStatus

def process_document_background(job_id: str, file_path: str):
    """
    This function runs in the background to process the document.
    It updates the job status in the in-memory store.
    """
    # 1. Get the job object from the in-memory store
    job = job_statuses.get(job_id)
    if not job:
        # This should not happen if the job was created correctly
        print(f"Error: Job with ID {job_id} not found.")
        return

    try:
        # 2. Read Document
        docx_tool = DocxReaderTool()
        parsed_document = docx_tool._run(file_path)
        
        # 3. Run AI Agent (Heavy processing)
        extraction_result = ExtractorCrewRunner.run_extraction(parsed_document)
        
        # 4. Map Data for Database
        # We get user/org/project info from the job object
        mapped_transactions = map_transactions(
            extracted_doc=extraction_result,
            user_id=job.user_id,
            org_id=job.org_id,
            project_id=job.project_id
        )

        # 5. Insert into Supabase
        # The original logic for saving to the database is preserved
        response = supabase.table("Transaction").insert(mapped_transactions).execute()
        
        # 6. Update job status to COMPLETED
        job.status = JobStatus.COMPLETED
        # Let's store the number of inserted rows as the result
        job.result = {"inserted_rows": len(response.data)}

    except Exception as e:
        # If any step fails, update job status to FAILED
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        # You can print the error for easier debugging in server logs
        print(f"Error processing job {job_id}: {e}")
        
    finally:
        # 7. Always update the timestamp and cleanup the temp file
        job.touch()
        if os.path.exists(file_path):
            os.remove(file_path)
