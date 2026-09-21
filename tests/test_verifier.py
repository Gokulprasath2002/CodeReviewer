from app.models import Finding
from app.verifier import Verifier


def test_verifier_deduplicates_and_filters():
    f = Finding("a.py", 2, "high", "Issue", "bad", confidence=.9)
    assert len(Verifier().verify([f, f])) == 1
    assert Verifier().verify([Finding("a.py", 2, "low", "Weak", "uncertain", confidence=.1)]) == []
