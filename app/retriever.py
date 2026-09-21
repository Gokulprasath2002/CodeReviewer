from typing import Dict, List


class ContextRetriever:
    def retrieve(self, files: Dict[str, str], graph: dict, findings: list, budget: int = 12000) -> dict:
        changed = list(files)
        related = set()
        for src, dst in graph.get("edges", []):
            if any(src.startswith(path + ":") for path in changed) or any(str(dst).startswith(path + ":") for path in changed):
                related.update((src, str(dst)))
        snippets = []
        used = 0
        for path, source in files.items():
            text = source[: max(0, budget - used)]
            snippets.append({"path": path, "role": "changed", "content": text})
            used += len(text)
            if used >= budget: break
        return {"changed_files": changed, "related_symbols": sorted(related), "snippets": snippets, "static_findings": [f.as_dict() for f in findings]}
