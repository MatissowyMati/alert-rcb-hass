"""Config flow for RSO."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
)

from .api import RSOApiClient, RSOApiError
from .const import (
    CATEGORIES,
    CONF_CATEGORY,
    CONF_NOTIFICATION_MODE,
    CONF_PROVINCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_CATEGORY,
    DEFAULT_NOTIFICATION_MODE,
    DEFAULT_PROVINCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    NOTIFICATION_MODES,
    PROVINCES,
)


def _select(options: dict[str, str]) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[{"value": key, "label": value} for key, value in options.items()],
            mode="dropdown",
        )
    )


class RSOConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle an RSO config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            province = user_input[CONF_PROVINCE]
            category = user_input[CONF_CATEGORY]
            await self.async_set_unique_id(f"{province}_{category}")
            self._abort_if_unique_id_configured()
            try:
                await RSOApiClient(async_get_clientsession(self.hass)).async_get_feed(
                    province, category
                )
            except RSOApiError:
                errors["base"] = "cannot_connect"
            else:
                title = user_input.pop(CONF_NAME) or f"RSO {PROVINCES[province]}"
                options = {
                    CONF_SCAN_INTERVAL: user_input.pop(CONF_SCAN_INTERVAL),
                    CONF_NOTIFICATION_MODE: user_input.pop(CONF_NOTIFICATION_MODE),
                }
                return self.async_create_entry(
                    title=title, data=user_input, options=options
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default="RSO"): str,
                vol.Required(CONF_PROVINCE, default=DEFAULT_PROVINCE): _select(
                    PROVINCES
                ),
                vol.Required(CONF_CATEGORY, default=DEFAULT_CATEGORY): _select(
                    CATEGORIES
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        mode="box",
                        unit_of_measurement="min",
                    )
                ),
                vol.Required(
                    CONF_NOTIFICATION_MODE, default=DEFAULT_NOTIFICATION_MODE
                ): SelectSelector(
                    SelectSelectorConfig(options=NOTIFICATION_MODES, mode="dropdown")
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry) -> RSOOptionsFlow:
        return RSOOptionsFlow()


class RSOOptionsFlow(OptionsFlow):
    """Handle configurable polling and notification settings."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        mode="box",
                        unit_of_measurement="min",
                    )
                ),
                vol.Required(
                    CONF_NOTIFICATION_MODE,
                    default=options.get(
                        CONF_NOTIFICATION_MODE, DEFAULT_NOTIFICATION_MODE
                    ),
                ): SelectSelector(
                    SelectSelectorConfig(options=NOTIFICATION_MODES, mode="dropdown")
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
