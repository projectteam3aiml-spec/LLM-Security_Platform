import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Security Platform API",
    version="1.0.0",
    description="Backend API for prompt threat detection, PHI masking, and policy enforcement."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router.api_router, prefix="/api/v1")


@app.on_event("startup")
def init_db_and_seed_admin():
    """Creates any missing tables and seeds a default admin user if the users
    table is empty. No Alembic migrations exist yet (see backend/requirements.txt),
    so this is the lean equivalent for a project at this stage; the same two
    calls are also exposed standalone -- see the README command for manual/CI use."""
    from app.db.base import Base
    from app.db.database import engine, SessionLocal
    from app.db.models import detected_entity, policy, prompt_analysis, user  # noqa: F401 -- registers models on Base.metadata
    from app.services.auth_service import ensure_default_admin

    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ensure_default_admin(db)
        finally:
            db.close()
    except Exception as e:
        # Don't crash the whole app if the DB isn't reachable yet at boot --
        # requests that need it will surface their own 500s until it is.
        logger.error(f"Startup DB init failed: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "llm-security-backend"}