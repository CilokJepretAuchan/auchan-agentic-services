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
    project_id: str
    user_id: str
    org_id: str
    status: JobStatus = JobStatus.PROCESSING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def touch(self):
        """Updates the updated_at timestamp."""
        self.updated_at = datetime.utcnow()