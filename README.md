# AI PR Reviewer

A repository-aware pull-request review MVP. It performs deterministic analysis before optional LLM reasoning, retrieves compressed context, verifies/deduplicates findings, persists review jobs in SQLite, and exposes an HTTP API.

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
uvicorn app.api:app --reload
```

Review a local checkout:

```bash
python -m app /path/to/checkout --base main --head HEAD
```

API: `POST /review` with `{"repo":"/path/to/checkout","pr":24,"base":"main","head":"HEAD"}`, then poll `GET /review/{job_id}`. `POST /github/webhook` accepts the normalized webhook payload. Set `GITHUB_WEBHOOK_SECRET` to enable HMAC validation.

Without `OPENAI_API_KEY`, the system is fully usable with deterministic Python findings. The LLM and GitHub publisher are explicit adapters and fail safely; no review is posted unless publishing is requested.

## Architecture

`api → pipeline → git service → AST/static analyzer → context retriever → optional LLM → verifier → SQLite/publisher`.

Run tests with `pytest`.
