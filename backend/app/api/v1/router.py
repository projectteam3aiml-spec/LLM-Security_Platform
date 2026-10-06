from fastapi import APIRouter
from app.api.v1 import analyze, auth, dashboard, logs, policies
# analysis.py (the legacy SecureRAGPipeline/FAISS/FLAN-T5 endpoint,
# /api/v1/analysis/analyze) was deleted: the 5-layer /api/v1/analyze pipeline
# is now the sole, canonical, JWT-protected entry point. app/services/analysis_service.py
# and app/ai_engine/secure_rag.py are unchanged and still present, but are now
# fully orphaned (nothing routes to them) rather than deleted outright.

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
api_router.include_router(logs.router, tags=["Threat Logs"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
# Include sub-routers here as we build them
# analyze.router and auth.router both already declare their own prefix
# internally; passing prefix= here too would double it up, so it's omitted
# for both. logs.router and dashboard.router also declare their own prefix.
api_router.include_router(analyze.router, tags=["Multi-Layer Security Analysis"])
# api_router.include_router(health.router, prefix="/health", tags=["System Health"])
