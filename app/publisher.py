from typing import List
from .models import Finding


class GitHubPublisher:
    def __init__(self, token: str = ""):
        self.token = token

    def publish(self, repo: str, pr: int, comments: List[Finding], summary: str) -> dict:
        if not self.token:
            return {"published": False, "reason": "GITHUB_TOKEN not configured"}
        # Deliberately safe default: publishing needs an explicit production adapter/configuration.
        return {"published": False, "reason": "GitHub publisher adapter is disabled in local mode"}
