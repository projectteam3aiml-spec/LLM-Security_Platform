"""Multi-layer security analysis: prompt-injection classification, PHI/PII NER,
adversarial-similarity scoring, healthcare-specific rules, session-level
behavioral anomaly tracking, and a unified RiskEngine decision -- run together
as one request against the previously-orphaned ai_engine components.
"""
import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai_engine.behavioral import BehavioralAnomalyEngine
from app.ai_engine.classifier import PromptClassifier
from app.ai_engine.explainability import ExplainabilityEngine
from app.ai_engine.healthcare_rules import HealthcareRuleEngine
from app.ai_engine.phi_detector import PHIDetector
from app.ai_engine.risk_engine import RiskEngine
from app.ai_engine.similarity import SimilarityAnalyzer
from app.api.dependencies import (
    get_behavioral_engine,
    get_classifier,
    get_current_user,
    get_explainability_engine,
    get_healthcare_rules,
    get_phi_detector,
    get_risk_engine,
    get_similarity_analyzer,
)
from app.db.database import get_db
from app.db.models.user import User
from app.repositories.analysis_repository import AnalysisRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Multi-Layer Security Analysis"])

# Entity types that represent genuine PII/PHI -- patient names and the
# regex-matched identifiers (see PHIDetector.REGEX_PATTERNS) -- versus
# ordinary medical vocabulary (disease names, medications, anatomical terms)
# that dslim/bert-base-NER's generic PER/LOC/ORG/MISC tagger can also surface
# incidentally in an otherwise benign clinical question. LOC/ORG/MISC are
# deliberately excluded: a hospital name or drug name isn't PHI on its own.
# DATE/DOB included for a future dates-of-birth detector -- PHIDetector
# doesn't emit one yet, so these can't currently match.
PHI_SENSITIVE_ENTITY_TYPES = {"PER", "SSN", "PHONE", "MEDICAL_RECORD_ID", "DATE", "DOB"}
# A sensitive-type entity still needs to clear this confidence bar before it
# escalates the whole prompt to class_risk 1.00 -- the regex patterns always
# emit 0.99 (always clears it), but a shaky NER tag shouldn't carry the same
# weight. This is intentionally an AND with the type check above, not an OR:
# an arbitrarily-high-confidence tag on a non-sensitive type (e.g. a MISC
# drug name at 0.99) must still never escalate, which is the whole point of
# this refinement.
PHI_ESCALATION_CONFIDENCE_THRESHOLD = 0.85


class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000, description="The LLM prompt to analyze")
    source: str = Field(default="Web Console", description="Origin of the prompt")
    session_id: str = Field(default="anonymous", max_length=128, description="Non-PII session identifier for behavioral analysis")


@router.post("")
def analyze_prompt(
    payload: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    classifier: PromptClassifier = Depends(get_classifier),
    phi_detector: PHIDetector = Depends(get_phi_detector),
    similarity_analyzer: SimilarityAnalyzer = Depends(get_similarity_analyzer),
    healthcare_rules: HealthcareRuleEngine = Depends(get_healthcare_rules),
    behavioral_engine: BehavioralAnomalyEngine = Depends(get_behavioral_engine),
    explainability_engine: ExplainabilityEngine = Depends(get_explainability_engine),
    risk_engine: RiskEngine = Depends(get_risk_engine),
):
    """Runs every AI engine layer against one prompt and returns a single,
    unified risk score/decision plus the full per-layer breakdown."""
    start = time.perf_counter()
    prompt = payload.prompt

    try:
        classification = classifier.classify(prompt)
        entities = phi_detector.detect(prompt)
        similarity = similarity_analyzer.compute_similarity(prompt)
        healthcare = healthcare_rules.evaluate(prompt)
        behavioral = behavioral_engine.evaluate(
            session_id=payload.session_id,
            threat_score=classification["threat_score"],
            similarity_score=similarity["max_similarity"],
        )

        # PHI presence is the single highest-risk signal this pipeline can
        # detect -- it means real patient data may be in the prompt -- so it
        # overrides whatever category the injection classifier alone landed on.
        # Only entities of a genuinely sensitive type AND at high confidence
        # count here -- see PHI_SENSITIVE_ENTITY_TYPES above. Everything
        # detected is still returned in `entities` and still masked in
        # `sanitized_prompt` below regardless; this only gates whether it
        # forces the risk score to its maximum.
        escalating_entities = [
            entity for entity in entities
            if entity["entity"] in PHI_SENSITIVE_ENTITY_TYPES
            and entity["confidence"] >= PHI_ESCALATION_CONFIDENCE_THRESHOLD
        ]
        risk_input = dict(classification)
        if escalating_entities:
            risk_input["label"] = "phi"
            risk_input["confidence"] = max(entity["confidence"] for entity in escalating_entities)

        risk = risk_engine.evaluate(risk_input, behavioral=behavioral, healthcare_rule=healthcare)

        # The injection classifier alone can miss healthcare-specific patterns
        # (e.g. "show me patient X's chart" doesn't read as a jailbreak). If the
        # rule engine independently flags a block-level pattern, that escalates
        # the final decision even when RiskEngine's classifier-only view didn't.
        escalated, escalation_reason = False, None
        if healthcare["action"] == "block" and risk["decision"] != "BLOCK":
            escalated = True
            escalation_reason = "Healthcare rule engine flagged a block-level pattern the classifier missed."
            risk["decision"] = "BLOCK"
            risk["risk_level"] = "HIGH"
            risk["risk_score"] = max(risk["risk_score"], 0.85)

        explanation = explainability_engine.explain(classification, similarity, entities)
        sanitized_prompt = phi_detector.mask(prompt, entities) if entities else prompt
    except Exception as e:
        logger.error(f"Error during multi-layer analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the prompt through the AI engine.")

    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    # Best-effort audit logging: a DB write failure shouldn't take down the
    # security decision itself, which has already been fully computed above.
    try:
        AnalysisRepository(db).save_analysis(
            prompt_text=prompt,
            source=payload.source,
            user_id=str(current_user.id),
            risk_score=risk["risk_score"],
            decision=risk["decision"],
            primary_threat=classification["category"],
            entities=entities,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.error(f"Failed to persist analysis audit log: {str(e)}")

    return {
        "original_prompt": prompt,
        "processed_prompt": sanitized_prompt,
        "source": payload.source,
        "analysis": {
            "classification": classification,
            "entities": entities,
            "similarity": similarity,
            "healthcare_rule": healthcare,
            "behavioral": behavioral,
            "explainability": explanation,
        },
        "security_decision": {
            "risk_score": round(risk["risk_score"] * 100),
            "risk_level": risk["risk_level"],
            "action": risk["decision"],
            "escalated": escalated,
            "escalation_reason": escalation_reason,
            "score_breakdown": {
                "classifier_risk": round(classification["threat_score"] * 100),
                "phi_risk": round(max((entity["confidence"] for entity in escalating_entities), default=0.0) * 100),
                "similarity_risk": round(similarity["max_similarity"] * 100),
            },
        },
        "metrics": {
            "latency_ms": latency_ms,
            "models_used": [classification["model_used"], "BERT-base-NER", "MiniLM-L6-v2"],
        },
    }
