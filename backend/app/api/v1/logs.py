from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.analysis import PromptAnalysisResponse
from app.repositories.analysis_repository import AnalysisRepository

router = APIRouter(prefix="/logs", tags=["Threat Logs"])


@router.get("", response_model=List[PromptAnalysisResponse])
def get_threat_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = AnalysisRepository(db)
    return repo.get_recent(limit=limit)
