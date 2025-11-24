from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router kamu
from api.routes.extract import router as extract_router

app = FastAPI(
    title="AuChan Agentic Service",
    version="1.0.0",
    description="AI-powered document parser & transaction extractor"
)

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

@app.get("/")
def read_root():
    return {"status": "running", "message": "Document Extraction API Ready"}

