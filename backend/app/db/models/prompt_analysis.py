import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class PromptAnalysis(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_system = Column(String, index=True)
    user_id = Column(String, index=True, nullable=True)

    prompt_text = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    decision = Column(String, index=True, nullable=False)  # RiskEngine's decision: ALLOW / REVIEW / BLOCK
    primary_threat = Column(String, nullable=True)
    latency_ms = Column(Float, nullable=True)

    flagged_entities = Column(JSON, default=list)

    detected_entities = relationship("DetectedEntity", back_populates="analysis", cascade="all, delete-orphan")
