from __future__ import annotations
import json, os
from typing import Any, Dict, List
from .models import Finding


class LLMReviewer:
    """Optional adapter. Without an API key, deterministic findings remain the review."""
    def __init__(self, api_key: str = "", model: str = "gpt-5"):
        self.api_key, self.model = api_key, model

    def review(self, context: Dict[str, Any], description: str = "") -> List[Finding]:
        if not self.api_key:
            return []
        # Keep the integration boundary explicit; production deployments can provide the OpenAI SDK.
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            prompt = {"repository_rules": "Review correctness, security, performance and maintainability only.", "pr_description": description, **context}
            response = client.responses.create(model=self.model, input=[{"role":"user", "content": "Return JSON with comments.\n" + json.dumps(prompt)}])
            data = json.loads(response.output_text)
            return [Finding(c["file"], int(c["line"]), c.get("severity", "medium"), c["title"], c["explanation"], "llm", float(c.get("confidence", .65))) for c in data.get("comments", [])]
        except Exception:
            return []
