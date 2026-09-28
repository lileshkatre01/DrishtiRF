from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

class HealthCheck(BaseModel):
    status: str
    project: str
    version: str

class CaptureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    format: str
    sample_rate: Optional[float]
    center_freq: Optional[float]
    n_samples: Optional[int]
    created_at: datetime

class JobCreate(BaseModel):
    capture_id: str

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    capture_id: str
    status: str
    stage: str
    progress: float
    created_at: datetime

class StageResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    stage: str
    json_result: Dict[str, Any]
    confidence: float
    explanation: Optional[str]
