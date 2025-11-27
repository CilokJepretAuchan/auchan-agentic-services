import os
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Pydantic Models
from core.models import Job

# Import router kamu
from api.routes.extract import router as extract_router
from api.routes.analysis import router as analysis_router

load_dotenv()
TEMP_UPLOAD_DIR = os.getenv("TEMP_UPLOAD_DIR")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="AuChan Agentic Service",
    version="1.0.0",
    description="AI-powered document parser & transaction extractor"
)

# This will act as an in-memory "database" for job statuses.
job_statuses: Dict[str, Job] = {}

# CORS (optional kalau tes lokal)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # untuk dev, produksi ganti domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(extract_router, prefix="/api", tags=["Extractor"])
app.include_router(analysis_router, prefix="/api", tags=["Analysis"])

@app.get("/")
def read_root():
    return {"status": "running", "message": "Document Extraction API Ready"}

