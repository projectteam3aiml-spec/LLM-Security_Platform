"""FastAPI-facing adapter for the single secure RAG pipeline."""
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from app.ai_engine.secure_rag import SecureRAGPipeline


class AnalysisService:
    """Expose SecureRAGPipeline results using the analysis API response shape."""

    def __init__(self, rag_pipeline: Optional[SecureRAGPipeline] = None):
        project_root = Path(__file__).resolve().parents[3]
        self.rag_pipeline = rag_pipeline or SecureRAGPipeline(project_root)

    async def analyze_prompt(self, prompt_text: str, source: str = "API Gateway", session_id: str = "anonymous") -> Dict[str, Any]:
        result = await asyncio.to_thread(self.rag_pipeline.answer, prompt_text)
        return {
            "original_prompt": prompt_text,
            "processed_prompt": prompt_text,
            "source": source,
            "analysis": {
                "classification": {
                    "label": result["predicted_class"],
                    "confidence": result["confidence"],
                    "probabilities": result.get("class_probabilities", {}),
                },
                "retrieved_documents": result.get("retrieved_documents", []),
                "answerability_status": result.get("validation_status"),
            },
            "security_decision": {
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "action": result["decision"],
                "flags": [],
                "score_breakdown": {
                    "class_risk": int(result["class_risk"] * 100),
                    "confidence_risk": int(result["confidence"] * 100),
                },
            },
            "response": result.get("final_answer"),
            "output_validation": {
                "status": result.get("validation_status"),
                "reasons": result.get("reasons", []),
                "detected_entities": result.get("detected_entities", []),
            },
            "execution": {
                "retrieval_performed": result.get("retrieval_performed", False),
                "llm_executed": result.get("llm_executed", False),
                "review_policy": result.get("review_policy"),
            },
        }