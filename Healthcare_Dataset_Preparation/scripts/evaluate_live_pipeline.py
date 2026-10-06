"""Live-pipeline decision benchmark -- in-process, no HTTP/ASGI layer at all.

Calls app.api.v1.analyze.analyze_prompt() directly as a plain Python
function, with its Depends() arguments resolved by hand using the same
factory functions FastAPI itself would call (app.api.dependencies.
get_classifier() etc.) -- NOT app.services.AnalysisService.analyze_prompt(),
which wraps the orphaned SecureRAGPipeline (secure_rag.py): a different
classifier-loading path, no PHI-override/healthcare-rule-escalation/
behavioral logic, a different embedder (BioBERT, not bge-small-en-v1.5), and
FLAN-T5 generation on every allowed row. router.py's own comment documents
that service as disconnected from the live endpoint, so benchmarking it
would silently score the wrong pipeline.

Calling the real analyze_prompt function object (rather than hand-
reimplementing its logic) means only dependency *wiring* is duplicated here,
not any decision logic -- so this can't silently drift from analyze.py's
actual behavior the way a from-scratch reimplementation could.

analyze_prompt is synchronous, so each call runs in a dedicated
ThreadPoolExecutor (not the default asyncio executor, which caps out around
os.cpu_count()+4 workers, and not Starlette/anyio's 40-token limiter either,
since this bypasses Starlette/ASGI entirely) and rows are dispatched in
explicit asyncio.gather() batches.

Run from inside the backend container:

    docker compose exec backend python \
        /app/Healthcare_Dataset_Preparation/scripts/evaluate_live_pipeline.py \
        --limit 10           # smoke-test timing
    docker compose exec backend python \
        /app/Healthcare_Dataset_Preparation/scripts/evaluate_live_pipeline.py
                              # full 2156-row run
"""
import argparse
import asyncio
import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, "/app/backend")  # the benchmark script's own dir isn't where the `app` package lives

from app.api.dependencies import (  # noqa: E402
    get_behavioral_engine,
    get_classifier,
    get_explainability_engine,
    get_healthcare_rules,
    get_phi_detector,
    get_risk_engine,
    get_similarity_analyzer,
)
from app.api.v1.analyze import AnalyzeRequest, analyze_prompt  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.db.models.user import User  # noqa: E402

DATASET = Path("/app/Healthcare_Dataset_Preparation/data/processed/security_test_processed.csv")
OUTPUT_DIR = Path("/app/Healthcare_Dataset_Preparation/outputs/evaluation")
ADMIN_EMAIL = "admin@example.com"


def process_row_sync(i: int, row: dict, user: User) -> dict:
    """Runs in a worker thread: one full analyze_prompt() call with its
    Depends() arguments resolved exactly as FastAPI would, each call on its
    own DB session so concurrent threads never share one."""
    db = SessionLocal()
    try:
        payload = AnalyzeRequest(prompt=row["prompt"], source="benchmark", session_id=f"bench-{i}")
        result = analyze_prompt(
            payload=payload,
            current_user=user,
            db=db,
            classifier=get_classifier(),
            phi_detector=get_phi_detector(),
            similarity_analyzer=get_similarity_analyzer(),
            healthcare_rules=get_healthcare_rules(),
            behavioral_engine=get_behavioral_engine(),
            explainability_engine=get_explainability_engine(),
            risk_engine=get_risk_engine(),
        )
        return {
            "index": i,
            "label_name": row["label_name"],
            "is_safe": row["is_safe"],
            "predicted_label": result["analysis"]["classification"]["label"],
            "action": result["security_decision"]["action"],
        }
    except Exception as exc:  # noqa: BLE001 -- keep the benchmark running past a bad row
        return {"index": i, "label_name": row["label_name"], "is_safe": row["is_safe"], "error": str(exc)}
    finally:
        db.close()


async def run_benchmark(rows: list, batch_size: int) -> list:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if user is None:
            raise RuntimeError(f"Seeded admin user {ADMIN_EMAIL} not found -- has the backend started at least once?")
    finally:
        db.close()

    # Prime every lazy singleton sequentially BEFORE dispatching concurrently.
    # Their getters guard construction with a plain `if _x is None` check and
    # no lock -- letting the first batch of worker threads race on that would
    # have several of them redundantly reconstruct the same model.
    print("Priming classifier / PHI detector / similarity model...", flush=True)
    get_classifier()
    get_phi_detector()
    get_similarity_analyzer()
    print("Models primed, starting batches.", flush=True)

    loop = asyncio.get_running_loop()
    results = [None] * len(rows)
    completed = 0
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        indexed_rows = list(enumerate(rows))
        for batch_start in range(0, len(indexed_rows), batch_size):
            batch = indexed_rows[batch_start: batch_start + batch_size]
            batch_results = await asyncio.gather(*[
                loop.run_in_executor(executor, process_row_sync, i, row, user)
                for i, row in batch
            ])
            for result in batch_results:
                results[result["index"]] = result
                completed += 1
            elapsed = time.perf_counter() - start
            print(f"[{completed}/{len(rows)}] elapsed={elapsed:.1f}s avg={elapsed / completed:.3f}s/row", flush=True)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only evaluate the first N rows (for timing smoke tests).")
    parser.add_argument("--batch-size", type=int, default=25, help="Rows dispatched per asyncio.gather() batch (20-30 recommended).")
    args = parser.parse_args()

    with DATASET.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    start = time.perf_counter()
    raw_results = asyncio.run(run_benchmark(rows, args.batch_size))
    elapsed_total = time.perf_counter() - start

    results = []
    tp = tn = fp = fn = errors = 0  # positive class = "threat" (is_safe == 0)
    for row, result in zip(rows, raw_results):
        if "error" in result:
            errors += 1
            results.append(result)
            continue

        ground_truth_safe = row["is_safe"] == "1"
        predicted_safe = result["action"] == "ALLOW"
        if not ground_truth_safe and not predicted_safe:
            tp += 1
        elif ground_truth_safe and predicted_safe:
            tn += 1
        elif ground_truth_safe and not predicted_safe:
            fp += 1
        else:
            fn += 1

        results.append({**result, "correct": ground_truth_safe == predicted_safe})
    scored = tp + tn + fp + fn
    accuracy = (tp + tn) / scored if scored else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_path = OUTPUT_DIR / "live_pipeline_decision_results.csv"
    with results_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "label_name", "is_safe", "predicted_label", "action", "correct", "error"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    summary = (
        "LIVE PIPELINE DECISION BENCHMARK (in-process direct call, bge-small-en-v1.5 + 0.35/0.65 thresholds + refined PHI escalation)\n"
        + "=" * 60 + "\n\n"
        f"Rows requested: {len(rows)}\n"
        f"Rows scored: {scored}\n"
        f"Rows errored (excluded from metrics): {errors}\n"
        f"Total wall time: {elapsed_total:.1f}s ({elapsed_total / max(len(rows), 1):.3f}s/row avg)\n\n"
        "Positive class = threat (is_safe == 0); predicted positive = action != ALLOW\n\n"
        f"Confusion matrix: TP={tp} FP={fp} FN={fn} TN={tn}\n\n"
        f"Accuracy:  {accuracy:.4f}\n"
        f"Precision: {precision:.4f}\n"
        f"Recall:    {recall:.4f}\n"
        f"F1-score:  {f1:.4f}\n\n"
        f">93% accuracy target: {'MET' if accuracy > 0.93 else 'NOT MET'} ({accuracy * 100:.2f}%)\n"
    )
    summary_path = OUTPUT_DIR / "live_pipeline_decision_metrics.txt"
    summary_path.write_text(summary, encoding="utf-8")

    print("\n" + summary)
    print(f"Per-row results written to {results_path}")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
