"""Regionalny System Ostrzegania integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RSOApiClient
from .const import PLATFORMS
from .coordinator import RSODataUpdateCoordinator

type RSOConfigEntry = ConfigEntry[RSODataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: RSOConfigEntry) -> bool:
    """Set up RSO from a config entry."""
    coordinator = RSODataUpdateCoordinator(
        hass,
        entry,
        RSOApiClient(async_get_clientsession(hass)),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(platform) for platform in PLATFORMS]
    )
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RSOConfigEntry) -> bool:
    """Unload an RSO config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, [Platform(platform) for platform in PLATFORMS]
    )


async def _async_reload_entry(hass: HomeAssistant, entry: RSOConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
