from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Defaults (pool_size=5, max_overflow=10 -> 15 max connections) were too low
# for concurrent /analyze traffic: every request holds a session for its
# full lifetime (Depends(get_db)), so 20-30 concurrent requests exhausted the
# pool and surfaced as sqlalchemy.exc.TimeoutError / 500s under load testing.
# Sized to 60 total to stay ahead of the live-pipeline benchmark's 50-100
# client-side concurrency -- note Starlette/anyio's default sync-endpoint
# thread pool caps actual concurrent executions at 40 regardless, so this
# already has headroom above that ceiling too.
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_size=30, max_overflow=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
