from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SAEnum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum
import uuid


def generate_uuid():
    return str(uuid.uuid4())

class QAStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PASSED = "passed"
    FAILED = "failed"
    FLAGGED = "flagged"

class FileType(str, enum.Enum):
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"

class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    country = Column(String(100), nullable=False)
    language = Column(String(100), nullable=False)
    total_submissions = Column(Integer, default=0)
    passed_submissions = Column(Integer, default=0)
    failed_submissions = Column(Integer, default=0)
    quality_score = Column(Float, default=100.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    submissions = relationship("Submission", back_populates="contributor")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=generate_uuid)
    contributor_id = Column(String, ForeignKey("contributors.id"), nullable=False)
    file_type = Column(SAEnum(FileType), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(SAEnum(QAStatus), default=QAStatus.PENDING, nullable=False)
    qa_score = Column(Float, nullable=True)
    file_metadata = Column(JSON, nullable=True)
    qa_results = Column(JSON, nullable=True)
    flag_reason = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    contributor = relationship("Contributor", back_populates="submissions")
