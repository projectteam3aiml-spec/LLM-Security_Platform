import pytest

from app.ai_engine.risk_engine import RiskEngine


@pytest.mark.parametrize(
    ("label", "confidence", "risk_score", "risk_level", "decision"),
    [
        ("safe", 0.99, 0.238, "LOW", "ALLOW"),
        ("suspicious", 0.99, 0.598, "MEDIUM", "REVIEW"),
        ("malicious", 0.99, 0.918, "HIGH", "BLOCK"),
        ("phi", 0.99, 0.998, "HIGH", "BLOCK"),
        ("jailbreak", 0.99, 0.958, "HIGH", "BLOCK"),
    ],
)
def test_phase7_risk_model(label, confidence, risk_score, risk_level, decision):
    result = RiskEngine().evaluate(label, confidence)

    assert result["risk_score"] == pytest.approx(risk_score)
    assert result["risk_level"] == risk_level
    assert result["decision"] == decision


def test_legacy_classifier_adapter_uses_phase7_model():
    result = RiskEngine().evaluate({"category": "Prompt Injection / Jailbreak", "confidence": 0.99})

    assert result["predicted_class"] == "jailbreak"
    assert result["decision"] == "BLOCK"