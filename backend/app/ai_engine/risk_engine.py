"""Authoritative Phase 7 risk-aware decision engine."""
from typing import Any, Dict, Union


class RiskEngine:
    """Convert a five-class security prediction into one policy decision."""

    CLASS_RISK = {
        "safe": 0.05,
        "suspicious": 0.50,
        "malicious": 0.90,
        "phi": 1.00,
        "jailbreak": 0.95,
    }
    SECURITY_WEIGHTS = {"class": 0.80, "confidence": 0.20}

    @staticmethod
    def _legacy_label(classification: Dict[str, Any]) -> str:
        """Adapt the legacy three-category API classifier to Phase 7 labels."""
        category = classification.get("category", "Safe Query")
        return {
            "Prompt Injection / Jailbreak": "jailbreak",
            "Suspicious Intent": "suspicious",
            "Safe Query": "safe",
        }.get(category, "suspicious")

    def evaluate(self, predicted_class: Union[str, Dict[str, Any]], confidence: float = None) -> Dict[str, Any]:
        """Calculate the sole project risk score and decision."""
        if isinstance(predicted_class, dict):
            classification = predicted_class
            label = classification.get("label") or self._legacy_label(classification)
            confidence = classification.get("confidence", 0.0) if confidence is None else confidence
        else:
            label = predicted_class

        label = str(label).lower()
        if label not in self.CLASS_RISK:
            raise ValueError(f"Unknown security class: {label}")
        if confidence is None:
            raise ValueError("confidence is required when passing a class label")

        confidence = max(0.0, min(1.0, float(confidence)))
        class_risk = self.CLASS_RISK[label]
        risk_score = self.SECURITY_WEIGHTS["class"] * class_risk + self.SECURITY_WEIGHTS["confidence"] * confidence
        if risk_score < 0.30:
            risk_level, decision = "LOW", "ALLOW"
        elif risk_score < 0.70:
            risk_level, decision = "MEDIUM", "REVIEW"
        else:
            risk_level, decision = "HIGH", "BLOCK"

        return {"predicted_class": label, "confidence": confidence, "class_risk": class_risk, "risk_score": risk_score, "risk_level": risk_level, "decision": decision}