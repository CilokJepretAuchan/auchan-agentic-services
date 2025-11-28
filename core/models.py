from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class JobStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(BaseModel):
    job_id: str

    # Optional identifiers (sometimes missing)
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    project_id: Optional[str] = None
    category_id: Optional[str] = None

    status: JobStatus = JobStatus.PROCESSING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def touch(self):
        """Updates the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


from pydantic import BaseModel
from typing import List, Optional

# --- Bagian Hard Data ---
class CategoryStat(BaseModel):
    name: str
    amount: float
    percentage: float

class ProjectStat(BaseModel):
    id: str
    name: str
    budget: float
    spent_this_month: float
    status: str # "Safe", "Warning", "Critical"

class FinancialContext(BaseModel):
    """
    Ini adalah context/data mentah yang sudah matang 
    untuk dikonsumsi oleh AI Agent atau Frontend.
    """
    org_name: str
    period: str # "11-2024"
    total_spent: float
    top_categories: List[CategoryStat]
    projects: List[ProjectStat]

# --- Bagian Output Akhir ---
class FullReportResponse(BaseModel):
    context: FinancialContext
    ai_narrative: str


class BuildReportRequest(BaseModel):
    org_id: str
    month: int
    year: int