from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    repo: str = Field(..., min_length=1, description="owner/name or local path")
    pr: int = Field(..., gt=0)
    base: str = "main"
    head: str = "HEAD"
    description: str = ""
    publish: bool = False


class ReviewJobResponse(BaseModel):
    job_id: str


class ReviewStatus(BaseModel):
    job_id: str
    status: str
    comments: int = 0
    error: Optional[str] = None


class WebhookPayload(BaseModel):
    repo: Optional[str] = None
    pr: Optional[int] = None
    base: Optional[str] = None
    head: Optional[str] = None
    action: Optional[str] = None


@dataclass
class Finding:
    file: str
    line: int
    severity: str
    title: str
    explanation: str
    source: str = "deterministic"
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    fingerprint: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ReviewResult:
    comments: List[Finding]
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)
