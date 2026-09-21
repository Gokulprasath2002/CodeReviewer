from app.api import app


def test_health():
    assert any(route.path == "/health" for route in app.routes)
    assert app.title == "AI PR Reviewer"
