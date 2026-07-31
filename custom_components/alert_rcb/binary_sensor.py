"""Binary sensors for RSO."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RSOConfigEntry
from .entity import RSOEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RSOConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([RSOCriticalAlertBinarySensor(entry.runtime_data)])


class RSOCriticalAlertBinarySensor(RSOEntity, BinarySensorEntity):
    """Whether the feed contains an RSO alarm alert."""

    _attr_translation_key = "critical_alert"
    _attr_icon = "mdi:alert-decagram"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "critical_alert")

    @property
    def is_on(self) -> bool:
        return any(alert.is_critical for alert in self.coordinator.data.active_alerts)

    @property
    def extra_state_attributes(self):
        critical = [
            {
                "id": alert.id,
                "title": alert.title,
                "valid_to": alert.valid_to.isoformat(),
                "provinces": list(alert.provinces),
            }
            for alert in self.coordinator.data.active_alerts
            if alert.is_critical
        ]
        return {"count": len(critical), "alerts": critical}
