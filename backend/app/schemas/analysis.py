from uuid import UUID
from pydantic import BaseModel, Field, computed_field
from typing import List, Dict, Any, Optional
from datetime import datetime

class EntitySchema(BaseModel):
    entity: str
    value: str
    start: int
    end: int
    confidence: float
    source: str

class ClassificationSchema(BaseModel):
    category: str
    confidence: float
    threat_score: float
    model_used: str

class SimilaritySchema(BaseModel):
    max_similarity: float
    matched_benchmark: Optional[str] = None
    embedding_dimension: int

class SecurityDecisionSchema(BaseModel):
    risk_score: int
    action: str
    flags: List[str]
    score_breakdown: Dict[str, int]

class AnalysisRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    source: str = Field(default="Web UI")

class AnalysisResponse(BaseModel):
    original_prompt: str
    processed_prompt: str
    source: str
    analysis: Dict[str, Any]
    security_decision: SecurityDecisionSchema
    metrics: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PromptAnalysisResponse(BaseModel):
    """Maps straight onto the PromptAnalysis ORM row for the Threat Logs /
    Overview "recent events" views -- the audit trail analyze.py writes,
    not the richer live /analyze response shape above."""
    id: UUID
    timestamp: datetime
    source_system: str
    user_id: Optional[str] = None
    prompt_text: str
    risk_score: float
    decision: str
    primary_threat: Optional[str] = None
    flagged_entities: List[str] = []
    latency_ms: Optional[float] = None

    @computed_field
    @property
    def risk_score_pct(self) -> int:
        """risk_score is stored as the raw 0..1 RiskEngine value -- expose the
        0..100 display form the frontend actually renders, same convention
        /analyze's own security_decision.risk_score already uses."""
        return round(self.risk_score * 100)

    class Config:
        from_attributes = True