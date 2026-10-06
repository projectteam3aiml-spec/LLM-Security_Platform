# Build context is ./backend (see docker-compose.yml). WORKDIR is /app/backend,
# not /app, specifically so that Healthcare_Dataset_Preparation/ can be mounted as
# a sibling at /app/Healthcare_Dataset_Preparation -- app/services/analysis_service.py
# resolves its project root as Path(__file__).resolve().parents[3], i.e. three levels
# above app/services/, which is /app/backend/app/services -> /app/backend -> /app.
FROM python:3.11-slim

# gcc/build-essential: safety net in case any dependency (spacy's thinc/blis, etc.)
# needs to compile from source on this platform instead of using a prebuilt wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefer-binary torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

RUN python -m spacy download en_core_web_sm
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
