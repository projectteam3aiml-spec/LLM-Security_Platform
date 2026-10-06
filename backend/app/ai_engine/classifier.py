from typing import Any, Dict

from app.ai_engine.model_loader import model_registry
from app.ai_engine.secure_rag import LABEL_MAP  # single source of truth, verified against the trained model's config.json

# Purely a display label for the legacy category/threat_score shape this
# endpoint (ExplainabilityEngine, ExplanationPanel.jsx) already expects --
# RiskEngine itself now consumes the native 5-class "label" directly.
CATEGORY_DISPLAY = {
    "safe": "Safe Query",
    "suspicious": "Suspicious Intent",
    "malicious": "Malicious Intent",
    "jailbreak": "Prompt Injection / Jailbreak",
    "phi": "PHI / PII Exposure Risk",
}
_SAFE_ID = next(class_id for class_id, name in LABEL_MAP.items() if name == "safe")

# Measured directly against Healthcare_Dataset_Preparation/data/processed/
# security_test_processed.csv (2156 rows) with the actual deployed weights --
# not the 93.28%/93.89% figures in training_summary.txt or the interview
# report, which are both from an earlier, superseded training run (wrong
# label ordering, different 2306-row test set). Re-measure and update this if
# the deployed weights change: eval script available on request.
TEST_ACCURACY = "89.9%"


class PromptClassifier:
    """Runs the project's own fine-tuned 5-class DistilBERT security classifier
    (safe/malicious/phi/jailbreak/suspicious) -- not an off-the-shelf binary
    injection detector."""

    def __init__(self):
        self.tokenizer = model_registry.injection_tokenizer
        self.model = model_registry.injection_model
        self.device = "cuda" if model_registry.device == 0 else "cpu"

    def classify(self, prompt: str) -> Dict[str, Any]:
        import torch
        import torch.nn.functional as F

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=256,  # matches the sequence length the model was trained/tokenized with
        ).to(self.device)

        with torch.no_grad():
            probabilities = F.softmax(self.model(**inputs).logits, dim=-1)[0]

        predicted_id = int(torch.argmax(probabilities).item())
        label = LABEL_MAP[predicted_id]
        confidence = round(float(probabilities[predicted_id].item()), 4)
        # Probability mass NOT on "safe" -- a single threat scalar that stays
        # meaningful regardless of which non-safe class actually won.
        threat_score = round(1.0 - float(probabilities[_SAFE_ID].item()), 4)

        return {
            "label": label,
            "category": CATEGORY_DISPLAY[label],
            "confidence": confidence,
            "threat_score": threat_score,
            "model_used": "DistilBERT-Security-Classifier",
            "model_test_accuracy": TEST_ACCURACY,
            "class_probabilities": {LABEL_MAP[i]: round(float(p.item()), 4) for i, p in enumerate(probabilities)},
        }
