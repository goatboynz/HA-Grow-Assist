"""Config flow for Grow Room Manager integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_CALENDAR_ENTITY,
    CONF_TODO_ENTITY,
)

_LOGGER = logging.getLogger(__name__)


class GrowRoomManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grow Room Manager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            room_id = user_input[CONF_ROOM_ID].lower().strip()
            
            # Check if room already exists
            await self.async_set_unique_id(f"{DOMAIN}_{room_id}")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input[CONF_ROOM_NAME],
                data={
                    CONF_ROOM_ID: room_id,
                    CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
                    CONF_CALENDAR_ENTITY: user_input.get(CONF_CALENDAR_ENTITY, ""),
                    CONF_TODO_ENTITY: user_input.get(CONF_TODO_ENTITY, ""),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ROOM_ID, default="f1"): str,
                vol.Required(CONF_ROOM_NAME, default="Flower Room 1"): str,
                vol.Optional(CONF_CALENDAR_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),
                vol.Optional(CONF_TODO_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="todo")
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return GrowRoomManagerOptionsFlow(config_entry)


class GrowRoomManagerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Grow Room Manager."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry data
            new_data = {**self.config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_ROOM_NAME,
                    default=self.config_entry.data.get(CONF_ROOM_NAME, "")
                ): str,
                vol.Optional(
                    CONF_CALENDAR_ENTITY,
                    default=self.config_entry.data.get(CONF_CALENDAR_ENTITY, "")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),
                vol.Optional(
                    CONF_TODO_ENTITY,
                    default=self.config_entry.data.get(CONF_TODO_ENTITY, "")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="todo")
                ),
            }),
        )
