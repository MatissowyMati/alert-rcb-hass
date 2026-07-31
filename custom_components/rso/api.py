"""Asynchronous client for the public RSO feed."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from aiohttp import ClientError, ClientSession

from .const import API_BASE_URL, API_TIMEOUT_SECONDS
from .models import RSOAlert, RSOFeed

_RSO_TIME_ZONE = ZoneInfo("Europe/Warsaw")


class RSOApiError(Exception):
    """Raised when the RSO API cannot be read."""


def _parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=_RSO_TIME_ZONE
        )
    except ValueError:
        return None


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def parse_alert(raw: dict[str, Any], category: str) -> RSOAlert | None:
    """Normalize one RSO response item."""
    valid_from = _parse_datetime(raw.get("valid_from"))
    valid_to = _parse_datetime(raw.get("valid_to"))
    try:
        alert_id = int(raw["id"])
    except (KeyError, TypeError, ValueError):
        return None
    if valid_from is None:
        valid_from = _parse_datetime(raw.get("created_at")) or datetime.now(
            _RSO_TIME_ZONE
        )
    if valid_to is None or valid_to <= valid_from:
        valid_to = valid_from.replace(microsecond=0) + timedelta(minutes=1)

    province_data = raw.get("provinces") or {}
    if isinstance(province_data, dict):
        provinces = tuple(
            str(value.get("name") or value.get("slug_name"))
            for value in province_data.values()
            if isinstance(value, dict) and (value.get("name") or value.get("slug_name"))
        )
    else:
        provinces = ()

    try:
        alarm_level = int(raw.get("rso_alarm") or 0)
    except (TypeError, ValueError):
        alarm_level = 0

    return RSOAlert(
        id=alert_id,
        title=str(raw.get("title") or f"RSO #{alert_id}"),
        shortcut=str(raw.get("shortcut") or ""),
        content=str(raw.get("content") or ""),
        alarm_level=alarm_level,
        valid_from=valid_from,
        valid_to=valid_to,
        created_at=_parse_datetime(raw.get("created_at")),
        updated_at=_parse_datetime(raw.get("updated_at")),
        provinces=provinces,
        longitude=_optional_float(raw.get("longitude")),
        latitude=_optional_float(raw.get("latitude")),
        river_name=str(raw.get("river_name") or "") or None,
        location_name=str(raw.get("location_name") or "") or None,
        water_level=str(raw.get("water_level_value") or "") or None,
        category=category,
    )


class RSOApiClient:
    """Client for komunikaty.tvp.pl."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_feed(self, province: str, category: str) -> RSOFeed:
        """Fetch the newest page for a province/category combination."""
        url = f"{API_BASE_URL}/komunikatyxml/{province}/{category}/1"
        try:
            async with asyncio.timeout(API_TIMEOUT_SECONDS):
                response = await self._session.get(url, params={"_format": "json"})
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (TimeoutError, ClientError, ValueError, TypeError) as err:
            raise RSOApiError(f"Unable to retrieve RSO feed: {err}") from err

        if not isinstance(payload, dict) or not isinstance(payload.get("newses"), list):
            raise RSOApiError("RSO returned an unexpected response")

        alerts = tuple(
            alert
            for item in payload["newses"]
            if isinstance(item, dict)
            and (alert := parse_alert(item, category)) is not None
        )
        alerts = tuple(sorted(alerts, key=lambda item: item.valid_from, reverse=True))
        pagination = payload.get("pagination") or {}
        try:
            total_items = int(pagination.get("totalitems", len(alerts)))
        except (TypeError, ValueError):
            total_items = len(alerts)
        return RSOFeed(alerts=alerts, total_items=total_items)
