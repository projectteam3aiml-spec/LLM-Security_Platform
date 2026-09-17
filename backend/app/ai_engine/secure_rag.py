"""Security-gated, evidence-grounded FAISS + FLAN-T5 RAG pipeline."""
from pathlib import Path
from typing import Any, Dict, List
import re
import numpy as np
import pandas as pd
from app.ai_engine.output_validator import OutputValidator
from app.ai_engine.risk_engine import RiskEngine

LABEL_MAP = {0: "safe", 1: "malicious", 2: "phi", 3: "jailbreak", 4: "suspicious"}

class SecureRAGPipeline:
    """Loads expensive resources lazily and never retrieves for BLOCK/REVIEW prompts."""
    def __init__(self, root: Path, review_policy: str = "abstain"):
        self.root, self.review_policy = Path(root), review_policy
        self.validator = OutputValidator()
        self.risk_engine = RiskEngine()
        self._loaded = False

    def load(self) -> None:
        import torch, faiss
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer
        from sentence_transformers import SentenceTransformer
        base = self.root / "Healthcare_Dataset_Preparation"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_dir = base / "outputs/security_classifier/best_model"
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.classifier = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device).eval()
        self.index = faiss.read_index(str(base / "outputs/faiss/knowledge_base.index"))
        self.kb = pd.read_csv(base / "data/processed/knowledge_base.csv")
        self.embedder = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")
        self.llm_tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.llm = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base").to(self.device).eval()
        if self.index.ntotal != len(self.kb): raise ValueError("FAISS and metadata counts differ")
        self._loaded = True

    def classify(self, prompt: str) -> Dict[str, Any]:
        import torch
        inputs = {key: value.to(self.device) for key, value in self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256).items()}
        with torch.no_grad(): probabilities = torch.softmax(self.classifier(**inputs).logits, dim=-1)[0].cpu().numpy()
        predicted_id = int(np.argmax(probabilities)); label = LABEL_MAP[predicted_id]; confidence = float(probabilities[predicted_id])
        risk = self.risk_engine.evaluate(label, confidence)
        return {**risk, "class_probabilities": {LABEL_MAP[i]: float(p) for i, p in enumerate(probabilities)}}

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        vector = self.embedder.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
        scores, indices = self.index.search(vector, top_k); rows = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx >= 0:
                row = self.kb.iloc[int(idx)]; rows.append({"rank": rank, "document_index": int(idx), "similarity_score": float(score), "source_dataset": row.get("source_dataset", "unknown"), "question": row.get("prompt", ""), "response": row.get("response", "")})
        return rows

    @staticmethod
    def _intent(text: str) -> str:
        text = text.lower()
        return next((label for label, words in {"symptoms":("symptom","sign"), "treatment":("treat","therapy","management"), "causes":("cause","why"), "diagnosis":("diagnos","test"), "definition":("what is","what are")}.items() if any(word in text for word in words)), "other")

    def select_evidence(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        intent = self._intent(query); content = re.sub(r"\b(what|are|is|the|symptoms?|signs?|how|treated?|treatment|of|for|a|an)\b", " ", query.lower()); content = " ".join(re.findall(r"[a-z0-9]+", content))
        selected = []
        for item in candidates:
            question = item["question"].lower(); intent_ok = intent == "other" or intent in self._intent(question) or (intent == "definition" and "what is" in question)
            entity_ok = len(content) >= 4 and (content in question or content in item["response"].lower())
            if intent_ok and entity_ok and item["similarity_score"] >= .35: selected.append(item)
        return selected[:3]

    def answer(self, prompt: str) -> Dict[str, Any]:
        if not self._loaded: self.load()
        security = self.classify(prompt)
        result = {"query": prompt, **security, "retrieval_performed": False, "llm_executed": False, "retrieved_documents": [], "generated_answer": None}
        if security["decision"] == "BLOCK":
            result.update({"validation_status": "BLOCKED", "final_answer": "This request cannot be processed safely."}); return result
        if security["decision"] == "REVIEW":
            result.update({"validation_status": "REVIEW", "review_policy": self.review_policy, "final_answer": "This request requires manual security review before it can be processed."}); return result
        candidates = self.retrieve(prompt, 5); result["retrieval_performed"] = True
        evidence = self.select_evidence(prompt, candidates); result["retrieved_documents"] = evidence
        if not evidence:
            result.update(self.validator.validate("", "", answerable=False)); return result
        context = "\n\n".join(f"Question: {item['question']}\nAnswer: {item['response']}" for item in evidence)
        instruction = f"Use only the supplied medical context. If it is insufficient, say so.\nContext: {context[:3500]}\nQuestion: {prompt}\nAnswer:"
        import torch
        inputs = self.llm_tokenizer(instruction, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
        with torch.no_grad(): output = self.llm.generate(**inputs, max_new_tokens=128, do_sample=False)
        generated = self.llm_tokenizer.decode(output[0], skip_special_tokens=True)
        result["generated_answer"] = generated; result.update(self.validator.validate(generated, context, answerable=True)); return result