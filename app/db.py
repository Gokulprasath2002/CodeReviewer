import json
import os
import sqlite3
from typing import Any, Dict, Optional


class Database:
    def __init__(self, path: str):
        self.path = path
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init()

    def init(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS pull_requests (
            id TEXT PRIMARY KEY, repo TEXT NOT NULL, pr_number INTEGER NOT NULL,
            base TEXT NOT NULL, head TEXT NOT NULL, status TEXT NOT NULL,
            error TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY, pr_id TEXT NOT NULL, comment_count INTEGER NOT NULL,
            confidence REAL NOT NULL, summary TEXT, metadata TEXT,
            FOREIGN KEY(pr_id) REFERENCES pull_requests(id)
        );
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, review_id TEXT NOT NULL, file TEXT NOT NULL,
            line INTEGER NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL,
            explanation TEXT NOT NULL, confidence REAL NOT NULL, accepted INTEGER DEFAULT 0,
            fingerprint TEXT NOT NULL, evidence TEXT,
            FOREIGN KEY(review_id) REFERENCES reviews(review_id)
        );
        """)
        self.conn.commit()

    def create_job(self, job_id: str, request: Dict[str, Any]) -> None:
        self.conn.execute("INSERT INTO pull_requests(id,repo,pr_number,base,head,status) VALUES(?,?,?,?,?,?)",
                          (job_id, request["repo"], request["pr"], request["base"], request["head"], "queued"))
        self.conn.commit()

    def update_job(self, job_id: str, status: str, error: Optional[str] = None) -> None:
        self.conn.execute("UPDATE pull_requests SET status=?, error=? WHERE id=?", (status, error, job_id))
        self.conn.commit()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM pull_requests WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    def save_review(self, review_id: str, job_id: str, comments: list, confidence: float, summary: str, metadata: dict) -> None:
        self.conn.execute("INSERT INTO reviews VALUES(?,?,?,?,?,?)", (review_id, job_id, len(comments), confidence, summary, json.dumps(metadata)))
        self.conn.executemany("INSERT INTO comments(review_id,file,line,severity,title,explanation,confidence,fingerprint,evidence) VALUES(?,?,?,?,?,?,?,?,?)",
            [(review_id, c.file, c.line, c.severity, c.title, c.explanation, c.confidence, c.fingerprint, json.dumps(c.evidence)) for c in comments])
        self.conn.commit()
