"""Event entity for immediate RSO alert automations."""

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RSOConfigEntry
from .entity import RSOEntity
from .models import RSOAlert


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RSOConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([RSOAlertEvent(entry.runtime_data)])


class RSOAlertEvent(RSOEntity, EventEntity):
    """Fires whenever the selected RSO feed changes."""

    _attr_translation_key = "alert_event"
    _attr_icon = "mdi:bell-alert"
    _attr_event_types = ["new_alert", "updated_alert"]

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "alert_event")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_alert_listener(self._async_handle_alert)
        )

    @callback
    def _async_handle_alert(self, event_type: str, alert: RSOAlert) -> None:
        self._trigger_event(event_type, alert.as_dict())
        self.async_write_ha_state()
