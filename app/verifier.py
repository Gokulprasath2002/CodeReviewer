from __future__ import annotations
import hashlib
from typing import Iterable, List
from .models import Finding


class Verifier:
    def __init__(self, threshold: float = 0.58):
        self.threshold = threshold

    def verify(self, findings: Iterable[Finding]) -> List[Finding]:
        out = []
        seen = set()
        for finding in findings:
            normalized = f"{finding.file}:{finding.line}:{finding.title.lower()}"
            finding.fingerprint = hashlib.sha256(normalized.encode()).hexdigest()[:16]
            if finding.fingerprint in seen: continue
            seen.add(finding.fingerprint)
            finding.confidence = min(1.0, max(0.0, finding.confidence + (0.05 if finding.source == "static" else 0)))
            if finding.confidence >= self.threshold:
                out.append(finding)
        return sorted(out, key=lambda x: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.severity, 4), x.file, x.line))
