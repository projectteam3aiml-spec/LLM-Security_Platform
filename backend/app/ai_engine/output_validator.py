"""Final safety validation for generated healthcare RAG answers."""
import re
from collections import Counter
from typing import Any, Dict, Iterable, List

class OutputValidator:
    SAFE_FALLBACK = "The available information is insufficient to answer this question."
    PHI_PATTERNS = {
        "EMAIL": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "PHONE": r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b",
        "DOB": r"\b(?:DOB|date of birth)\s*[:#-]?\s*(?:\d{1,2}[/-]){2}\d{2,4}\b",
        "MEDICAL_RECORD_ID": r"\b(?:MRN|medical record(?: number)?|patient ID)\s*[:#-]?\s*[A-Z0-9-]{4,}\b",
    }
    INSTRUCTION_LEAKS = ("ignore previous instructions", "answer only the question asked", "do not use unrelated information", "system prompt", "bypass safety")
    UNSAFE_PATTERNS = ("reveal patient records", "disable safety restrictions", "api key", "security control bypass")

    def validate(self, answer: str, context: str = "", answerable: bool = True) -> Dict[str, Any]:
        answer = (answer or "").strip()
        if not answer:
            return self._result("EMPTY_OUTPUT", self.SAFE_FALLBACK)
        if not answerable:
            return self._result("INSUFFICIENT_EVIDENCE", self.SAFE_FALLBACK)
        if len(answer) > 2500:
            return self._result("UNSAFE_OUTPUT", self.SAFE_FALLBACK, ["Answer exceeds maximum length."])
        lowered = answer.lower()
        entities = self.detect_phi(answer)
        if entities:
            return self._result("PHI_DETECTED", self.SAFE_FALLBACK, ["Potential PHI detected."], entities)
        if any(marker in lowered for marker in self.INSTRUCTION_LEAKS):
            return self._result("UNSAFE_OUTPUT", self.SAFE_FALLBACK, ["Instruction leakage detected."])
        if any(marker in lowered for marker in self.UNSAFE_PATTERNS):
            return self._result("UNSAFE_OUTPUT", self.SAFE_FALLBACK, ["Unsafe security content detected."])
        if self._repetitive(answer):
            return self._result("UNSAFE_OUTPUT", self.SAFE_FALLBACK, ["Excessive sentence repetition detected."])
        if context and not self._grounded(answer, context):
            return self._result("UNSUPPORTED", self.SAFE_FALLBACK, ["Major answer terms are not supported by retrieved context."])
        return self._result("VALID", answer)

    def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        entities = []
        for entity_type, pattern in self.PHI_PATTERNS.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                entities.append({"entity": entity_type, "value": match.group(0), "start": match.start(), "end": match.end(), "confidence": 0.99})
        for match in re.finditer(r"\b(?:patient|mr\.?|ms\.?|mrs\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", text):
            entities.append({"entity": "PERSON", "value": match.group(0), "start": match.start(), "end": match.end(), "confidence": 0.70})
        return entities

    @staticmethod
    def _tokens(text: str) -> set:
        stop = {"the", "and", "with", "from", "that", "this", "are", "for", "was", "were", "into", "your", "you", "what", "when", "where", "how", "can", "may", "has", "have", "will", "does", "not"}
        return {word for word in re.findall(r"[a-z]{4,}", text.lower()) if word not in stop}

    def _grounded(self, answer: str, context: str) -> bool:
        answer_terms, context_terms = self._tokens(answer), self._tokens(context)
        return not answer_terms or len(answer_terms & context_terms) / len(answer_terms) >= 0.45

    @staticmethod
    def _repetitive(answer: str) -> bool:
        sentences = [re.sub(r"\W+", " ", item).strip().lower() for item in re.split(r"[.!?]+", answer) if item.strip()]
        return len(sentences) >= 3 and len(set(sentences)) / len(sentences) < 0.67

    @staticmethod
    def _result(status: str, final_answer: str, reasons: Iterable[str] = (), entities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"validation_status": status, "final_answer": final_answer, "reasons": list(reasons), "detected_entities": entities or []}