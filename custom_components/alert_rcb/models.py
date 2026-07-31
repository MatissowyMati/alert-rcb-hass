"""Data models for RSO."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class RSOAlert:
    """A normalized RSO alert."""

    id: int
    title: str
    shortcut: str
    content: str
    alarm_level: int
    valid_from: datetime
    valid_to: datetime
    created_at: datetime | None
    updated_at: datetime | None
    provinces: tuple[str, ...]
    longitude: float | None
    latitude: float | None
    river_name: str | None
    location_name: str | None
    water_level: str | None
    category: str

    @property
    def is_critical(self) -> bool:
        """Return whether RSO marks this alert for alarm distribution."""
        return self.alarm_level > 0

    @property
    def fingerprint(self) -> str:
        """Return a stable revision fingerprint."""
        revision = self.updated_at or self.created_at or self.valid_from
        return f"{self.id}:{revision.isoformat()}"

    @property
    def url(self) -> str:
        """Return the public RSO portal URL."""
        return "https://komunikaty.tvp.pl/"

    def as_dict(self) -> dict[str, Any]:
        """Return event and state attributes."""
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.shortcut,
            "description": self.content,
            "alarm_level": self.alarm_level,
            "critical": self.is_critical,
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "provinces": list(self.provinces),
            "category": self.category,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "river_name": self.river_name,
            "location_name": self.location_name,
            "water_level": self.water_level,
            "url": self.url,
        }


@dataclass(frozen=True, slots=True)
class RSOFeed:
    """Current RSO feed data."""

    alerts: tuple[RSOAlert, ...]
    total_items: int

    @property
    def active_alerts(self) -> tuple[RSOAlert, ...]:
        """Return alerts currently within their validity window."""
        now = datetime.now().astimezone()
        return tuple(
            alert for alert in self.alerts if alert.valid_from <= now < alert.valid_to
        )
