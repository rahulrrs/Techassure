from app.services.risk import _rating


def test_risk_rating_boundaries():
    assert _rating(10) == "Low"
    assert _rating(30) == "Medium"
    assert _rating(60) == "High"
    assert _rating(90) == "Critical"
