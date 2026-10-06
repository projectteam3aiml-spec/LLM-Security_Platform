"""Persists analyze_prompt results as an audit trail: one PromptAnalysis row
plus one DetectedEntity row per detected entity. Targets the real models
(prompt_analysis.py, detected_entity.py) -- the old version of this file
referenced app.db.models.base.PromptLog, which never existed anywhere in
this codebase.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.detected_entity import DetectedEntity
from app.db.models.prompt_analysis import PromptAnalysis

# PromptClassifier's CATEGORY_DISPLAY labels, bucketed into the three
# risk tiers the Overview risk-distribution donut shows. Kept here (not
# imported from classifier.py) so this repository has no AI-engine/torch
# import dependency -- it only ever touches primary_threat as a stored string.
_SAFE_CATEGORIES = {"Safe Query"}
_SUSPICIOUS_CATEGORIES = {"Suspicious Intent"}


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_analysis(
        self,
        prompt_text: str,
        source: str,
        user_id: Optional[str],
        risk_score: float,
        decision: str,
        primary_threat: str,
        entities: List[Dict[str, Any]],
        latency_ms: Optional[float] = None,
    ) -> PromptAnalysis:
        analysis = PromptAnalysis(
            source_system=source,
            user_id=user_id,
            prompt_text=prompt_text,
            risk_score=risk_score,
            decision=decision,
            primary_threat=primary_threat,
            flagged_entities=[entity["entity"] for entity in entities],
            latency_ms=latency_ms,
        )
        self.db.add(analysis)
        self.db.flush()  # assigns analysis.id before building child rows

        for entity in entities:
            self.db.add(
                DetectedEntity(
                    analysis_id=analysis.id,
                    entity_type=entity["entity"],
                    value=entity["value"],
                    start_char=entity["start"],
                    end_char=entity["end"],
                    confidence_score=entity["confidence"],
                )
            )

        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_recent(self, limit: int = 50) -> List[PromptAnalysis]:
        return self.db.query(PromptAnalysis).order_by(PromptAnalysis.timestamp.desc()).limit(limit).all()

    def get_stats(self) -> Dict[str, Any]:
        total = self.db.query(func.count(PromptAnalysis.id)).scalar() or 0
        blocked = (
            self.db.query(func.count(PromptAnalysis.id))
            .filter(PromptAnalysis.decision == "BLOCK")
            .scalar()
            or 0
        )
        phi_masked = (
            self.db.query(func.count(DetectedEntity.id))
            .scalar()
            or 0
        )
        avg_latency = self.db.query(func.avg(PromptAnalysis.latency_ms)).scalar()
        return {
            "prompts_analyzed": total,
            "threats_blocked": blocked,
            "phi_entities_masked": phi_masked,
            "avg_latency_ms": round(avg_latency, 1) if avg_latency is not None else None,
        }

    def get_risk_distribution(self) -> Dict[str, float]:
        rows = (
            self.db.query(PromptAnalysis.primary_threat, func.count(PromptAnalysis.id))
            .group_by(PromptAnalysis.primary_threat)
            .all()
        )
        buckets = {"safe": 0, "suspicious": 0, "malicious": 0}
        for primary_threat, count in rows:
            if primary_threat in _SAFE_CATEGORIES:
                buckets["safe"] += count
            elif primary_threat in _SUSPICIOUS_CATEGORIES:
                buckets["suspicious"] += count
            else:
                buckets["malicious"] += count

        total = sum(buckets.values())
        if total == 0:
            return {"safe": 0.0, "suspicious": 0.0, "malicious": 0.0}
        return {key: round(value / total * 100, 1) for key, value in buckets.items()}

    def get_p95_latency_ms(self) -> Optional[float]:
        """Python-side percentile (not a SQL percentile_cont) -- simplest
        portable option given the row counts this table realistically holds
        early in the product's life; revisit if that assumption stops holding."""
        samples = sorted(
            value
            for (value,) in self.db.query(PromptAnalysis.latency_ms)
            .filter(PromptAnalysis.latency_ms.isnot(None))
            .all()
        )
        if not samples:
            return None
        index = min(int(len(samples) * 0.95), len(samples) - 1)
        return round(samples[index], 1)

    def get_hourly_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Buckets BLOCK/REVIEW counts by hour over the trailing window. Python-side
        bucketing (not a SQL date_trunc) keeps this portable and simple for the
        low row-counts this table will realistically hold early on."""
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            self.db.query(PromptAnalysis.timestamp, PromptAnalysis.decision)
            .filter(PromptAnalysis.timestamp >= since)
            .all()
        )

        buckets: Dict[str, Dict[str, int]] = {}
        for timestamp, decision in rows:
            label = timestamp.strftime("%H:00")
            bucket = buckets.setdefault(label, {"blocked": 0, "flagged": 0})
            if decision == "BLOCK":
                bucket["blocked"] += 1
            elif decision == "REVIEW":
                bucket["flagged"] += 1

        now_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        ordered_labels = [(now_hour - timedelta(hours=offset)).strftime("%H:00") for offset in range(hours - 1, -1, -1)]
        return [
            {"time": label, **buckets.get(label, {"blocked": 0, "flagged": 0})}
            for label in ordered_labels
        ]
