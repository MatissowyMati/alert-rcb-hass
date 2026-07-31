"""Calendar feed for RSO alerts."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RSOConfigEntry
from .entity import RSOEntity
from .models import RSOAlert


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RSOConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([RSOCalendar(entry.runtime_data)])


def _to_calendar_event(alert: RSOAlert) -> CalendarEvent:
    location = alert.location_name or ", ".join(alert.provinces) or None
    description = f"{alert.shortcut}\n\n{alert.content}\n\n{alert.url}"
    return CalendarEvent(
        start=alert.valid_from,
        end=alert.valid_to,
        summary=alert.title,
        description=description,
        location=location,
        uid=str(alert.id),
    )


class RSOCalendar(RSOEntity, CalendarEntity):
    """Calendar containing alerts in the selected feed."""

    _attr_translation_key = "alerts_calendar"
    _attr_icon = "mdi:calendar-alert"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "calendar")

    @property
    def event(self) -> CalendarEvent | None:
        now = datetime.now().astimezone()
        candidates = [
            alert for alert in self.coordinator.data.alerts if alert.valid_to > now
        ]
        if not candidates:
            return None
        active_or_next = min(
            candidates,
            key=lambda item: (item.valid_from > now, item.valid_from),
        )
        return _to_calendar_event(active_or_next)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        alerts = [
            alert
            for alert in self.coordinator.data.alerts
            if alert.valid_to > start_date and alert.valid_from < end_date
        ]
        return [
            _to_calendar_event(alert)
            for alert in sorted(alerts, key=lambda item: item.valid_from)
        ]
