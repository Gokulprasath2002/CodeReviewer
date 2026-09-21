from __future__ import annotations
import ast
import re
from typing import Dict, Iterable, List, Tuple
from .models import Finding


class PythonAnalyzer:
    """Small deterministic analyzer; findings are facts fed to the reviewer."""
    def analyze(self, files: Dict[str, str]) -> Tuple[List[Finding], dict, dict]:
        findings: List[Finding] = []
        graph = {"nodes": [], "edges": []}
        symbols = {}
        for path, source in files.items():
            try:
                tree = ast.parse(source, filename=path)
            except SyntaxError as exc:
                findings.append(Finding(path, exc.lineno or 1, "high", "Syntax error", str(exc), confidence=.98))
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    key = f"{path}:{node.name}"
                    graph["nodes"].append(key); symbols[node.name] = key
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            graph["edges"].append((f"{path}:{node.name}", child.func.id))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                    findings.append(Finding(path, node.lineno, "high", "Dynamic code execution", f"{node.func.id} executes code dynamically and can enable code injection.", evidence=["AST call to dynamic execution"], confidence=.95))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format" and node.args:
                    pass
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    findings.append(Finding(path, node.lineno, "medium", "Bare exception handler", "Catching every exception can hide programming errors and interrupt cancellation.", confidence=.82))
            for lineno, line in enumerate(source.splitlines(), 1):
                if re.search(r"\b(password|secret|api[_-]?key|token)\s*=\s*['\"]", line, re.I):
                    findings.append(Finding(path, lineno, "high", "Hard-coded credential", "A credential-like value is committed in source; load it from a secret manager or environment.", confidence=.9))
                if "except Exception" in line and "pass" in source.splitlines()[min(lineno, len(source.splitlines()))-1: min(lineno+2, len(source.splitlines()))]:
                    findings.append(Finding(path, lineno, "medium", "Exception is discarded", "This handler appears to discard an exception, reducing observability.", confidence=.78))
        return findings, graph, symbols
