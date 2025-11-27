import os
import pandas as pd

# Supabase and service imports
from core.supabase import supabase
from services.anomaly_detector import TransactionAnomalyDetector

from core.memory import job_statuses
from core.models import JobStatus

def run_anomaly_pipeline_background(job_id: str):
    """
    This function runs the full anomaly detection pipeline in the background.
    It fetches data from Supabase, runs the analysis, and saves the results.
    """
    # 1. Get the job object from the in-memory store
    job = job_statuses.get(job_id)
    if not job:
        print(f"Error: Job with ID {job_id} not found.")
        return

    try:
        # 2. Fetch data from Supabase
        print(f"Job {job_id}: Fetching data from Supabase...")
        transactions_response = supabase.table("Transaction").select("*").execute()
        projects_response = supabase.table("Project").select("*").execute()

        # Convert to DataFrame
        df_transactions = pd.DataFrame(transactions_response.data)
        df_projects = pd.DataFrame(projects_response.data)

        if df_transactions.empty or df_projects.empty:
            raise ValueError("Transaction or Project data is empty. Cannot run analysis.")

        # 3. Run the anomaly detection pipeline
        print(f"Job {job_id}: Running anomaly detection pipeline...")
        detector = TransactionAnomalyDetector(df_transactions, df_projects)
        anomaly_reports = detector.run_pipeline()
        
        # 4. Save results to Supabase
        if anomaly_reports:
            print(f"Job {job_id}: Found {len(anomaly_reports)} anomalies. Saving to database...")
            supabase.table("AnomalyReport").insert(anomaly_reports).execute()
        else:
            print(f"Job {job_id}: No anomalies found.")

        # 5. Update job status to COMPLETED
        job.status = JobStatus.COMPLETED
        job.result = {"anomalies_found": len(anomaly_reports)}

    except Exception as e:
        # If any step fails, update job status to FAILED
        print(f"Error processing job {job_id}: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        
    finally:
        # 6. Always update the timestamp
        job.touch()
        print(f"Job {job_id}: Processing finished with status: {job.status.value}")
