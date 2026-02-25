from sqlalchemy import Column, DateTime, Enum, String, func
from source.core.models import Model
import enum

class PipelineStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"

class Pipeline(Model):
    """
    Tracks background pipelines/jobs
    """
    __tablename__ = "pipeline"

    start_time = Column(DateTime, nullable=False, default=func.now(), index=True)
    end_time = Column(DateTime, nullable=True, index=True)

    pipeline_type = Column(String(64), nullable=False, index=True)

    status = Column(Enum(PipelineStatus, name="pipeline_status"), nullable=False, default=PipelineStatus.pending, index=True)
