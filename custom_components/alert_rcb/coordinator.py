"""Update coordinator for RSO."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta

from homeassistant.components.persistent_notification import async_create
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RSOApiClient, RSOApiError
from .const import (
    CONF_CATEGORY,
    CONF_NOTIFICATION_MODE,
    CONF_PROVINCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_CATEGORY,
    DEFAULT_NOTIFICATION_MODE,
    DEFAULT_PROVINCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_NEW_ALERT,
    EVENT_UPDATED_ALERT,
)
from .models import RSOAlert, RSOFeed

_LOGGER = logging.getLogger(__name__)
_STORAGE_VERSION = 1


class RSODataUpdateCoordinator(DataUpdateCoordinator[RSOFeed]):
    """Coordinate RSO polling and new-alert delivery."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: RSOApiClient
    ) -> None:
        options = entry.options
        minutes = int(options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"Alert RCB {entry.title}",
            update_interval=timedelta(minutes=minutes),
            always_update=False,
        )
        self.api = api
        self.entry = entry
        self._store = Store[dict[str, str]](
            hass, _STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}.seen"
        )
        self._seen: dict[str, str] | None = None
        self._alert_listeners: list[Callable[[str, RSOAlert], None]] = []

    async def _async_update_data(self) -> RSOFeed:
        province = self.entry.data.get(CONF_PROVINCE, DEFAULT_PROVINCE)
        category = self.entry.data.get(CONF_CATEGORY, DEFAULT_CATEGORY)
        try:
            feed = await self.api.async_get_feed(province, category)
        except RSOApiError as err:
            raise UpdateFailed(str(err)) from err

        if self._seen is None:
            stored = await self._store.async_load()
            self._seen = stored if isinstance(stored, dict) else {}
            if not self._seen:
                self._seen = {str(alert.id): alert.fingerprint for alert in feed.alerts}
                await self._store.async_save(self._seen)
                return feed

        changed = False
        for alert in reversed(feed.alerts):
            key = str(alert.id)
            old_fingerprint = self._seen.get(key)
            if old_fingerprint == alert.fingerprint:
                continue
            event_type = (
                EVENT_NEW_ALERT if old_fingerprint is None else EVENT_UPDATED_ALERT
            )
            self._seen[key] = alert.fingerprint
            changed = True
            self.hass.bus.async_fire(event_type, alert.as_dict())
            for listener in tuple(self._alert_listeners):
                listener(
                    "new_alert" if old_fingerprint is None else "updated_alert",
                    alert,
                )
            self._notify(alert, event_type)

        if changed:
            self._seen = dict(list(self._seen.items())[-500:])
            await self._store.async_save(self._seen)
        return feed

    def _notify(self, alert: RSOAlert, event_type: str) -> None:
        mode = self.entry.options.get(CONF_NOTIFICATION_MODE, DEFAULT_NOTIFICATION_MODE)
        if mode == "none" or (mode == "critical" and not alert.is_critical):
            return
        prefix = "Nowy" if event_type == EVENT_NEW_ALERT else "Zaktualizowany"
        provinces = ", ".join(alert.provinces) or "Polska"
        async_create(
            self.hass,
            f"{alert.shortcut or alert.content}\n\nRegion: {provinces}\n"
            f"Ważne do: {alert.valid_to.isoformat()}\n\n"
            f"[Otwórz komunikat]({alert.url})",
            title=f"{prefix} Alert RCB: {alert.title}",
            notification_id=f"alert_rcb_{self.entry.entry_id}_{alert.id}",
        )

    @callback
    def async_add_alert_listener(
        self, listener: Callable[[str, RSOAlert], None]
    ) -> Callable[[], None]:
        """Register a listener for new and updated alerts."""
        self._alert_listeners.append(listener)

        @callback
        def remove_listener() -> None:
            self._alert_listeners.remove(listener)

        return remove_listener
