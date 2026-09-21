from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class DiffFile:
    path: str
    status: str
    patch: str


class GitService:
    def __init__(self, repo: str):
        self.repo = os.path.abspath(repo)
        if not os.path.isdir(os.path.join(self.repo, ".git")):
            raise ValueError("repo must be a local git checkout for the local MVP")

    def _run(self, *args: str) -> str:
        return subprocess.check_output(["git", "-C", self.repo, *args], text=True, stderr=subprocess.STDOUT)

    def diff(self, base: str, head: str) -> List[DiffFile]:
        merge = self._run("merge-base", base, head).strip()
        raw = self._run("diff", "--find-renames", "--unified=80", f"{merge}..{head}", "--")
        files = []
        current = None
        chunks = []
        for line in raw.splitlines(True):
            if line.startswith("diff --git "):
                if current:
                    files.append(DiffFile(current, "modified", "".join(chunks)))
                parts = line.split()
                current = parts[3][2:] if len(parts) > 3 else "unknown"
                chunks = [line]
            elif current:
                chunks.append(line)
        if current:
            files.append(DiffFile(current, "modified", "".join(chunks)))
        return files

    def file_at(self, revision: str, path: str) -> str:
        try:
            return self._run("show", f"{revision}:{path}")
        except subprocess.CalledProcessError:
            return ""

    def changed_source(self, base: str, head: str) -> dict:
        return {f.path: self.file_at(head, f.path) for f in self.diff(base, head) if f.path.endswith((".py", ".js", ".ts"))}
