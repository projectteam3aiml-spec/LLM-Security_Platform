from typing import Optional

from pydantic import BaseModel


class DashboardStats(BaseModel):
    prompts_analyzed: int
    threats_blocked: int
    phi_entities_masked: int
    avg_latency_ms: Optional[float] = None


class RiskDistribution(BaseModel):
    safe: float
    suspicious: float
    malicious: float


class ThreatTrendPoint(BaseModel):
    time: str
    blocked: int
    flagged: int


class PipelineStatus(BaseModel):
    classifier_loaded: bool
    phi_detector_loaded: bool
    similarity_analyzer_loaded: bool


class ModelHealth(BaseModel):
    status: str
    prompts_analyzed: int
    detection_accuracy: str
    end_to_end_accuracy: str
    p95_latency_ms: Optional[float] = None
    p95_sample_size: int = 0
    uptime_seconds: float
    cpu_usage_pct: float
    memory_usage_pct: float
    pipeline: PipelineStatus
