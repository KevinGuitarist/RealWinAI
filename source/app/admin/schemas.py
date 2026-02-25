from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from source.app.admin.models import PipelineStatus

class PipelineBase(BaseModel):
    pipeline_type: str = Field(..., max_length=64)
    status: PipelineStatus = PipelineStatus.pending
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class PipelineCreate(PipelineBase):
    pipeline_type: str

class PipelineUpdate(BaseModel):
    status: Optional[PipelineStatus] = None
    end_time: Optional[datetime] = None

class PipelineOut(BaseModel):
    id: int
    pipeline_type: str
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime]
    create_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True