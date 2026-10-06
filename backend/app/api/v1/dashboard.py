"""Overview/Model Health metrics computed from the real PromptAnalysis audit
trail analyze.py writes, plus live psutil system stats -- not the mock/random
figures the now-removed standalone dashboard_service.py draft used to return.
"""
import time

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai_engine.classifier import TEST_ACCURACY
from app.api.dependencies import get_current_user, get_model_load_status
from app.db.database import get_db
from app.db.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.dashboard import DashboardStats, ModelHealth, RiskDistribution, ThreatTrendPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Process-wide, set once at import time (module is imported exactly once per
# worker on startup) -- good enough for a single-uvicorn-process dev/demo
# deployment; swap for a shared store if this ever runs with multiple workers.
_PROCESS_START = time.time()

# Decision-level accuracy of the full /analyze pipeline (classifier + PHI
# escalation + thresholds together) against security_test_processed.csv's
# is_safe ground truth, via Healthcare_Dataset_Preparation/scripts/
# evaluate_live_pipeline.py -- distinct from TEST_ACCURACY above, which is
# the DistilBERT classifier alone, in isolation from PHI escalation/
# thresholds. Measured 2026-10-06 against the bge-small-en-v1.5 similarity
# model, 0.35/0.65 RiskEngine thresholds, and the sensitive-entity-type PHI
# escalation filter. Re-measure and update this if any of those change.
END_TO_END_ACCURACY = "86.5%"


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalysisRepository(db).get_stats()


@router.get("/risk-distribution", response_model=RiskDistribution)
def get_risk_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalysisRepository(db).get_risk_distribution()


@router.get("/threat-trends", response_model=list[ThreatTrendPoint])
def get_threat_trends(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalysisRepository(db).get_hourly_trends(hours=hours)


@router.get("/model-health", response_model=ModelHealth)
def get_model_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = AnalysisRepository(db)
    stats = repo.get_stats()
    return ModelHealth(
        status="Operational",
        prompts_analyzed=stats["prompts_analyzed"],
        detection_accuracy=TEST_ACCURACY,
        end_to_end_accuracy=END_TO_END_ACCURACY,
        p95_latency_ms=repo.get_p95_latency_ms(),
        uptime_seconds=time.time() - _PROCESS_START,
        cpu_usage_pct=psutil.cpu_percent(interval=0.1),
        memory_usage_pct=psutil.virtual_memory().percent,
        pipeline=get_model_load_status(),
    )
