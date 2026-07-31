"""Base entity for RSO."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import RSODataUpdateCoordinator


class RSOEntity(CoordinatorEntity[RSODataUpdateCoordinator]):
    """Base RSO entity."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: RSODataUpdateCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Telewizja Polska",
            model="Regionalny System Ostrzegania",
            name=coordinator.entry.title,
            configuration_url="https://komunikaty.tvp.pl/",
        )
