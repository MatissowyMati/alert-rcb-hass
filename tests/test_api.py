"""Tests for RSO response parsing."""

from custom_components.rso.api import parse_alert


def test_parse_alert() -> None:
    alert = parse_alert(
        {
            "id": "42",
            "title": "Burze/2",
            "shortcut": "Silne burze",
            "content": "Treść",
            "rso_alarm": "1",
            "valid_from": "2026-07-31 12:00:00",
            "valid_to": "2026-07-31 14:00:00",
            "created_at": "2026-07-31 11:50:00",
            "updated_at": "2026-07-31 11:55:00",
            "longitude": "21.0",
            "latitude": "52.0",
            "provinces": {"7": {"name": "Mazowieckie"}},
        },
        "meteorologiczne",
    )
    assert alert is not None
    assert alert.id == 42
    assert alert.is_critical
    assert alert.provinces == ("Mazowieckie",)
    assert alert.category == "meteorologiczne"


def test_parse_alert_rejects_missing_id() -> None:
    assert parse_alert({}, "wszystkie") is None
