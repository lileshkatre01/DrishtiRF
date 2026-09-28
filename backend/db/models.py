from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Capture(Base):
    __tablename__ = "captures"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    format = Column(String, nullable=False)  # cs8, cs16, cf32, wav, sigmf
    sample_rate = Column(Float, nullable=True)
    center_freq = Column(Float, nullable=True)
    n_samples = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="capture", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    capture_id = Column(String, ForeignKey("captures.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    stage = Column(String, default="INGESTION") # INGESTION, SPECTRAL, AMC, DEMOD, JOINT_SEARCH, CORRELATION
    progress = Column(Float, default=0.0)       # 0.0 to 100.0
    created_at = Column(DateTime, default=datetime.utcnow)

    capture = relationship("Capture", back_populates="jobs")
    stage_results = relationship("StageResult", back_populates="job", cascade="all, delete-orphan")
    frames = relationship("Frame", back_populates="job", cascade="all, delete-orphan")


class StageResult(Base):
    __tablename__ = "stage_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    stage = Column(String, nullable=False)
    json_result = Column(JSON, nullable=False)
    confidence = Column(Float, default=1.0)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="stage_results")


class Frame(Base):
    __tablename__ = "frames"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    offset = Column(Integer, nullable=False)
    sync_word = Column(String, nullable=True)
    header_hex = Column(Text, nullable=True)
    payload_hex = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="frames")
