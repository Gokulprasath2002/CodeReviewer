from __future__ import annotations
import uuid
from typing import Callable, Optional
from .analyzer import PythonAnalyzer
from .git_service import GitService
from .llm import LLMReviewer
from .models import ReviewRequest, ReviewResult
from .retriever import ContextRetriever
from .verifier import Verifier


class ReviewPipeline:
    def __init__(self, llm: Optional[LLMReviewer] = None):
        self.analyzer = PythonAnalyzer(); self.retriever = ContextRetriever(); self.verifier = Verifier(); self.llm = llm or LLMReviewer()

    def run(self, request: ReviewRequest, progress: Optional[Callable[[str], None]] = None) -> ReviewResult:
        progress = progress or (lambda _: None)
        progress("analyzing diff")
        git = GitService(request.repo)
        files = git.changed_source(request.base, request.head)
        findings, graph, _ = self.analyzer.analyze(files)
        progress("building context")
        context = self.retriever.retrieve(files, graph, findings)
        progress("reviewing")
        findings.extend(self.llm.review(context, request.description))
        comments = self.verifier.verify(findings)
        summary = f"Reviewed {len(files)} changed source file(s); found {len(comments)} actionable comment(s)."
        return ReviewResult(comments, summary, {"files": list(files), "graph": graph, "pipeline": "deterministic+optional-llm"})
