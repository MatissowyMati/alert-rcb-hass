"""Button entities for RSO."""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RSOConfigEntry
from .entity import RSOEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RSOConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([RSORefreshButton(entry.runtime_data)])


class RSORefreshButton(RSOEntity, ButtonEntity):
    """Request an immediate feed refresh."""

    _attr_translation_key = "refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "refresh")

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
