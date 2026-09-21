from __future__ import annotations
import hashlib, hmac, json, threading, uuid
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from .config import settings
from .db import Database
from .llm import LLMReviewer
from .models import ReviewRequest, ReviewJobResponse, ReviewStatus, WebhookPayload
from .pipeline import ReviewPipeline
from .publisher import GitHubPublisher

app = FastAPI(title="AI PR Reviewer", version="1.0.0")
db = Database(settings.database_path)
pipeline = ReviewPipeline(LLMReviewer(settings.openai_api_key, settings.openai_model))


def _run(job_id: str, request: ReviewRequest) -> None:
    try:
        db.update_job(job_id, "running")
        result = pipeline.run(request)
        review_id = str(uuid.uuid4())
        confidence = sum(c.confidence for c in result.comments) / len(result.comments) if result.comments else 1.0
        db.save_review(review_id, job_id, result.comments, confidence, result.summary, result.metadata)
        if request.publish or settings.publish_reviews:
            GitHubPublisher(settings.github_token).publish(request.repo, request.pr, result.comments, result.summary)
        db.update_job(job_id, "completed")
    except Exception as exc:
        db.update_job(job_id, "failed", str(exc))


@app.get("/health")
def health(): return {"status": "ok"}


@app.post("/review", response_model=ReviewJobResponse, status_code=202)
def create_review(request: ReviewRequest):
    job_id = str(uuid.uuid4()); db.create_job(job_id, request.dict())
    threading.Thread(target=_run, args=(job_id, request), daemon=True).start()
    return {"job_id": job_id}


@app.get("/review/{job_id}", response_model=ReviewStatus)
def review_status(job_id: str):
    row = db.get_job(job_id)
    if not row: raise HTTPException(404, "review job not found")
    count = db.conn.execute("SELECT comment_count FROM reviews WHERE pr_id=? ORDER BY rowid DESC LIMIT 1", (job_id,)).fetchone()
    return {"job_id": job_id, "status": row["status"], "comments": count[0] if count else 0, "error": row["error"]}


@app.post("/github/webhook", status_code=202)
def github_webhook(payload: WebhookPayload, x_hub_signature_256: Optional[str] = Header(default=None)):
    raw = json.dumps(payload.dict(), separators=(",", ":")).encode()
    if settings.webhook_secret:
        expected = "sha256=" + hmac.new(settings.webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
        if not x_hub_signature_256 or not hmac.compare_digest(expected, x_hub_signature_256): raise HTTPException(401, "invalid signature")
    if payload.action not in (None, "opened", "synchronize", "reopened"): return {"accepted": False, "reason": "event ignored"}
    if not payload.repo or not payload.pr: raise HTTPException(400, "repo and pr are required")
    request = ReviewRequest(repo=payload.repo, pr=payload.pr, base=payload.base or "main", head=payload.head or "HEAD")
    return create_review(request)
