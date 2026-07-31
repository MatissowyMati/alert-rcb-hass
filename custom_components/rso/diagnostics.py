"""Diagnostics for RSO."""

from homeassistant.core import HomeAssistant

from . import RSOConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: RSOConfigEntry
) -> dict:
    coordinator = entry.runtime_data
    return {
        "entry": {"data": dict(entry.data), "options": dict(entry.options)},
        "last_update_success": coordinator.last_update_success,
        "feed_total": coordinator.data.total_items,
        "returned_alerts": len(coordinator.data.alerts),
        "alerts": [alert.as_dict() for alert in coordinator.data.alerts],
    }
