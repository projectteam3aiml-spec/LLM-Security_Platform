"""Decision-factor explanations for security assessments."""
from typing import Any, Dict, List


class ExplainabilityEngine:
    """Expose factors actually available from the active analysis pipeline."""
    def explain(self, classification: Dict[str, Any], similarity: Dict[str, Any], entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        factors = [
            {"feature": "classifier", "value": classification.get("threat_score", 0.0), "detail": classification.get("category", "Unknown")},
            {"feature": "semantic_similarity", "value": similarity.get("max_similarity", 0.0), "detail": similarity.get("matched_benchmark") or "No benchmark match"},
            {"feature": "phi_entities", "value": len(entities), "detail": f"{len(entities)} entity or entities detected"},
        ]
        return {"method": "decision-factor attribution", "top_factors": sorted(factors, key=lambda factor: factor["value"], reverse=True)}