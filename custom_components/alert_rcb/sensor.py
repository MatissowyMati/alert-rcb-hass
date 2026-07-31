"""Sensors for the RSO integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RSOConfigEntry
from .entity import RSOEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RSOConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(
        [
            RSOActiveAlertsSensor(entry.runtime_data),
            RSOLatestAlertSensor(entry.runtime_data),
        ]
    )


class RSOActiveAlertsSensor(RSOEntity, SensorEntity):
    """Number of alerts returned by the selected feed."""

    _attr_translation_key = "active_alerts"
    _attr_icon = "mdi:alert-box"
    _attr_native_unit_of_measurement = "alerts"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "active_alerts")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.active_alerts)

    @property
    def extra_state_attributes(self):
        return {
            "total_feed_items": self.coordinator.data.total_items,
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "alarm_level": alert.alarm_level,
                    "valid_to": alert.valid_to.isoformat(),
                    "provinces": list(alert.provinces),
                }
                for alert in self.coordinator.data.active_alerts
            ],
        }


class RSOLatestAlertSensor(RSOEntity, SensorEntity):
    """Latest alert summary."""

    _attr_translation_key = "latest_alert"
    _attr_icon = "mdi:message-alert"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "latest_alert")

    @property
    def native_value(self) -> str | None:
        alerts = self.coordinator.data.alerts
        return alerts[0].title if alerts else None

    @property
    def extra_state_attributes(self):
        alerts = self.coordinator.data.alerts
        return alerts[0].as_dict() if alerts else {}
