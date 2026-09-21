from app.analyzer import PythonAnalyzer


def test_analyzer_finds_security_and_bare_except():
    findings, graph, _ = PythonAnalyzer().analyze({"payment.py": "API_KEY = 'secret'\ndef pay():\n    try:\n        eval('1')\n    except:\n        pass\n"})
    titles = {f.title for f in findings}
    assert "Hard-coded credential" in titles
    assert "Dynamic code execution" in titles
    assert "Bare exception handler" in titles
    assert graph["nodes"]
