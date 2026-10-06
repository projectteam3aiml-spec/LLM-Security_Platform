import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.ai_engine.behavioral import BehavioralAnomalyEngine
from app.ai_engine.classifier import PromptClassifier
from app.ai_engine.explainability import ExplainabilityEngine
from app.ai_engine.healthcare_rules import HealthcareRuleEngine
from app.ai_engine.phi_detector import PHIDetector
from app.ai_engine.risk_engine import RiskEngine
from app.ai_engine.similarity import SimilarityAnalyzer
from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models.user import User

# Cheap, model-free engines: safe to instantiate eagerly as module-level
# singletons. BehavioralAnomalyEngine in particular needs to be a singleton --
# its per-session event history has to persist across requests to detect
# bursts/repeats at all.
_risk_engine = RiskEngine()
_healthcare_rules = HealthcareRuleEngine()
_behavioral_engine = BehavioralAnomalyEngine()
_explainability_engine = ExplainabilityEngine()

# PromptClassifier/PHIDetector/SimilarityAnalyzer each pull a tokenizer/model/
# pipeline out of model_registry inside __init__, which triggers a real HF
# download+load. Instantiating them eagerly at module import time would bring
# back the exact startup-crash landmine that app/ai_engine/model_loader.py's
# lazy rewrite was meant to fix -- so these three stay lazily constructed on
# first request instead.
_classifier = None
_phi_detector = None
_similarity_analyzer = None


def get_risk_engine() -> RiskEngine:
    """Dependency to inject the Risk Engine into API routes."""
    return _risk_engine


def get_classifier() -> PromptClassifier:
    global _classifier
    if _classifier is None:
        _classifier = PromptClassifier()
    return _classifier


def get_phi_detector() -> PHIDetector:
    global _phi_detector
    if _phi_detector is None:
        _phi_detector = PHIDetector()
    return _phi_detector


def get_similarity_analyzer() -> SimilarityAnalyzer:
    global _similarity_analyzer
    if _similarity_analyzer is None:
        _similarity_analyzer = SimilarityAnalyzer()
    return _similarity_analyzer


def get_healthcare_rules() -> HealthcareRuleEngine:
    return _healthcare_rules


def get_model_load_status() -> dict:
    """Reports whether each lazily-constructed AI engine has actually been
    instantiated yet (i.e. served at least one /analyze request), for the
    Model Health page's pipeline-stage indicators. Reading these globals
    doesn't trigger a load -- that's the whole point of the lazy pattern
    these three are built with (see the comment above their declaration)."""
    return {
        "classifier_loaded": _classifier is not None,
        "phi_detector_loaded": _phi_detector is not None,
        "similarity_analyzer_loaded": _similarity_analyzer is not None,
    }


def get_behavioral_engine() -> BehavioralAnomalyEngine:
    return _behavioral_engine


def get_explainability_engine() -> ExplainabilityEngine:
    return _explainability_engine


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user
