"""Deterministic safety rules for healthcare prompts."""
import re
from typing import Any, Dict, List

class HealthcareRuleEngine:
    RULES = (
        ("emergency_triage", 0.85, r"\b(chest pain|can't breathe|cannot breathe|suicid(?:e|al)|overdos(?:e|ing)|severe bleeding)\b", "Potential emergency symptom; direct the user to emergency services."),
        ("prescription_request", 0.60, r"\b(prescribe|prescription|dosage|dose|increase my (?:drug|medication)|stop (?:taking )?my medication)\b", "Medication decisions require a licensed clinician."),
        ("diagnosis_request", 0.45, r"\b(diagnose me|what disease do i have|tell me if i have|definitive diagnosis)\b", "Do not present generated content as a definitive diagnosis."),
        ("record_exfiltration", 0.90, r"\b(show|give|retrieve|list|export).{0,40}\b(patient (?:record|chart|history)|medical record|ehr)\b", "Request may seek another person's protected health information."),
    )
    def evaluate(self, prompt: str) -> Dict[str, Any]:
        matches: List[Dict[str, Any]] = []
        for rule_id, severity, pattern, guidance in self.RULES:
            if re.search(pattern, prompt.lower(), flags=re.IGNORECASE):
                matches.append({"rule_id": rule_id, "severity": severity, "guidance": guidance})
        risk_score = max((match["severity"] for match in matches), default=0.0)
        return {"risk_score": risk_score, "action": "block" if risk_score >= 0.85 else ("warn" if matches else "allow"), "matched_rules": matches}