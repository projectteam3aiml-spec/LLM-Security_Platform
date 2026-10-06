"""Final safety validation for generated healthcare RAG answers."""
import re
from typing import Any, Dict, Iterable, List

class OutputValidator:
    SAFE_FALLBACK = "The available information is insufficient to answer this question."

    # Kept as regex: these are fixed, deterministic formats where a pattern match IS the signal.
    PHI_PATTERNS = {
        "EMAIL": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "PHONE": r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b",
        "DOB": r"\b(?:DOB|date of birth)\s*[:#-]?\s*(?:\d{1,2}[/-]){2}\d{2,4}\b",
        "MEDICAL_RECORD_ID": r"\b(?:MRN|medical record(?: number)?|patient ID)\s*[:#-]?\s*[A-Z0-9-]{4,}\b",
    }
    INSTRUCTION_LEAKS = ("ignore previous instructions", "answer only the question asked", "do not use unrelated information", "system prompt", "bypass safety")
    UNSAFE_PATTERNS = ("reveal patient records", "disable safety restrictions", "api key", "security control bypass")

    # Free-form entities (names, dates, organizations, addresses) aren't reliably regex-matchable
    # (the old "patient|mr|ms|mrs <Name>" pattern only caught names with a preceding title), so these
    # go through spaCy NER instead. GPE/LOC/FAC are folded into ADDRESS since en_core_web_sm has no
    # single "address" label.
    SPACY_MODEL = "en_core_web_sm"
    SPACY_ENTITY_MAP = {"PERSON": "PERSON", "DATE": "DATE", "ORG": "ORG", "GPE": "ADDRESS", "LOC": "ADDRESS", "FAC": "ADDRESS"}

    # NLI label order verified against the model's own config.json id2label (0/1/2 = contradiction/
    # entailment/neutral) rather than assumed. Thresholds are calibrated starting points, not exact.
    NLI_MODEL = "cross-encoder/nli-deberta-v3-xsmall"
    CONTRADICTION_THRESHOLD = 0.55
    ENTAILMENT_SUPPORT_THRESHOLD = 0.40

    _nlp = None
    _nli_model = None

    @classmethod
    def _get_nlp(cls):
        if cls._nlp is None:
            import spacy
            try:
                cls._nlp = spacy.load(cls.SPACY_MODEL)
            except OSError as exc:
                raise RuntimeError(f"spaCy model '{cls.SPACY_MODEL}' is not installed. Run: python -m spacy download {cls.SPACY_MODEL}") from exc
        return cls._nlp

    @classmethod
    def _get_nli_model(cls):
        if cls._nli_model is None:
            from sentence_transformers import CrossEncoder
            cls._nli_model = CrossEncoder(cls.NLI_MODEL)
        return cls._nli_model

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
        if context:
            grounding = self._semantic_grounding(answer, context)
            if not grounding["grounded"]:
                reason = "Answer contradicts the retrieved medical context." if grounding["contradicted"] else "Major answer claims are not supported by retrieved context."
                return self._result("UNSUPPORTED", self.SAFE_FALLBACK, [reason])
        return self._result("VALID", answer)

    def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        entities = []
        for entity_type, pattern in self.PHI_PATTERNS.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                entities.append({"entity": entity_type, "value": match.group(0), "start": match.start(), "end": match.end(), "confidence": 0.99})
        doc = self._get_nlp()(text)
        for ent in doc.ents:
            mapped = self.SPACY_ENTITY_MAP.get(ent.label_)
            if mapped is None:
                continue
            if any(e["start"] < ent.end_char and ent.start_char < e["end"] for e in entities):
                continue  # already covered by a deterministic regex match
            entities.append({"entity": mapped, "value": ent.text, "start": ent.start_char, "end": ent.end_char, "confidence": 0.85})
        return entities

    def _semantic_grounding(self, answer: str, context: str) -> Dict[str, bool]:
        nlp = self._get_nlp()
        answer_sentences = [sent.text.strip() for sent in nlp(answer).sents if sent.text.strip()]
        context_chunks = [sent.text.strip() for sent in nlp(context).sents if sent.text.strip()]
        if not answer_sentences or not context_chunks:
            return {"grounded": not answer_sentences, "contradicted": False}
        model = self._get_nli_model()
        contradicted, grounded = False, True
        for sentence in answer_sentences:
            pairs = [(chunk, sentence) for chunk in context_chunks]
            scores = model.predict(pairs, apply_softmax=True)  # columns: [contradiction, entailment, neutral]
            max_contradiction = float(max(row[0] for row in scores))
            max_entailment = float(max(row[1] for row in scores))
            if max_contradiction >= self.CONTRADICTION_THRESHOLD:
                contradicted, grounded = True, False
            elif max_entailment < self.ENTAILMENT_SUPPORT_THRESHOLD:
                grounded = False
        return {"grounded": grounded, "contradicted": contradicted}

    @staticmethod
    def _repetitive(answer: str) -> bool:
        sentences = [re.sub(r"\W+", " ", item).strip().lower() for item in re.split(r"[.!?]+", answer) if item.strip()]
        return len(sentences) >= 3 and len(set(sentences)) / len(sentences) < 0.67

    @staticmethod
    def _result(status: str, final_answer: str, reasons: Iterable[str] = (), entities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"validation_status": status, "final_answer": final_answer, "reasons": list(reasons), "detected_entities": entities or []}
