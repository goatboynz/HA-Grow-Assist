"""Config flow for Grow Room Manager integration."""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_CALENDAR_ENTITY,
    CONF_TODO_ENTITY,
    CONF_START_DATE,
    CONF_START_DATE_ENTITY,
    CONF_ROOM_TYPE,
    ROOM_TYPE_FLOWER,
    ROOM_TYPE_VEG,
)

_LOGGER = logging.getLogger(__name__)


class GrowRoomManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grow Room Manager."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._room_type: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - choose room type."""
        if user_input is not None:
            self._room_type = user_input[CONF_ROOM_TYPE]
            if self._room_type == ROOM_TYPE_FLOWER:
                return await self.async_step_flower_room()
            else:
                return await self.async_step_veg_room()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ROOM_TYPE, default=ROOM_TYPE_FLOWER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=ROOM_TYPE_FLOWER, label="Flower Room (84-day cycle)"),
                            selector.SelectOptionDict(value=ROOM_TYPE_VEG, label="Veg Room (continuous batches)"),
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }),
        )

    async def async_step_flower_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle flower room setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            room_id = user_input[CONF_ROOM_ID].lower().strip().replace(" ", "_")
            
            await self.async_set_unique_id(f"{DOMAIN}_{room_id}")
            self._abort_if_unique_id_configured()
            
            start_date = user_input.get(CONF_START_DATE)
            if isinstance(start_date, date):
                start_date = start_date.isoformat()
            
            return self.async_create_entry(
                title=user_input[CONF_ROOM_NAME],
                data={
                    CONF_ROOM_ID: room_id,
                    CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
                    CONF_ROOM_TYPE: ROOM_TYPE_FLOWER,
                    CONF_START_DATE: start_date,
                    CONF_START_DATE_ENTITY: user_input.get(CONF_START_DATE_ENTITY, ""),
                    CONF_CALENDAR_ENTITY: user_input.get(CONF_CALENDAR_ENTITY, ""),
                    CONF_TODO_ENTITY: user_input.get(CONF_TODO_ENTITY, ""),
                },
            )

        return self.async_show_form(
            step_id="flower_room",
            data_schema=vol.Schema({
                vol.Required(CONF_ROOM_ID, default="f1"): str,
                vol.Required(CONF_ROOM_NAME, default="Flower Room 1"): str,
                vol.Optional(CONF_START_DATE): selector.DateSelector(),
                vol.Optional(CONF_START_DATE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["input_datetime", "sensor"],
                        multiple=False
                    )
                ),
                vol.Optional(CONF_CALENDAR_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),
                vol.Optional(CONF_TODO_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="todo")
                ),
            }),
            errors=errors,
        )

    async def async_step_veg_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle veg room setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            room_id = user_input[CONF_ROOM_ID].lower().strip().replace(" ", "_")
            
            await self.async_set_unique_id(f"{DOMAIN}_{room_id}")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input[CONF_ROOM_NAME],
                data={
                    CONF_ROOM_ID: room_id,
                    CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
                    CONF_ROOM_TYPE: ROOM_TYPE_VEG,
                    CONF_CALENDAR_ENTITY: user_input.get(CONF_CALENDAR_ENTITY, ""),
                    CONF_TODO_ENTITY: user_input.get(CONF_TODO_ENTITY, ""),
                },
            )

        return self.async_show_form(
            step_id="veg_room",
            data_schema=vol.Schema({
                vol.Required(CONF_ROOM_ID, default="veg"): str,
                vol.Required(CONF_ROOM_NAME, default="Veg Room"): str,
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
    """Handle options flow - edit room settings including start date."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the room options."""
        room_type = self.config_entry.data.get(CONF_ROOM_TYPE, ROOM_TYPE_FLOWER)
        
        if room_type == ROOM_TYPE_VEG:
            return await self.async_step_veg_options(user_input)
        return await self.async_step_flower_options(user_input)

    async def async_step_flower_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage flower room options."""
        if user_input is not None:
            start_date = user_input.get(CONF_START_DATE)
            if isinstance(start_date, date):
                start_date = start_date.isoformat()
            
            new_data = {
                **self.config_entry.data,
                CONF_START_DATE: start_date,
                CONF_START_DATE_ENTITY: user_input.get(CONF_START_DATE_ENTITY, ""),
                CONF_ROOM_NAME: user_input.get(CONF_ROOM_NAME, self.config_entry.data.get(CONF_ROOM_NAME)),
                CONF_CALENDAR_ENTITY: user_input.get(CONF_CALENDAR_ENTITY, ""),
                CONF_TODO_ENTITY: user_input.get(CONF_TODO_ENTITY, ""),
            }
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, 
                data=new_data,
                title=new_data[CONF_ROOM_NAME]
            )
            
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        current_start = self.config_entry.data.get(CONF_START_DATE)
        current_start_entity = self.config_entry.data.get(CONF_START_DATE_ENTITY, "")
        
        return self.async_show_form(
            step_id="flower_options",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_ROOM_NAME,
                    default=self.config_entry.data.get(CONF_ROOM_NAME, "")
                ): str,
                vol.Optional(
                    CONF_START_DATE,
                    default=current_start if current_start else None
                ): selector.DateSelector(),
                vol.Optional(
                    CONF_START_DATE_ENTITY,
                    default=current_start_entity
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["input_datetime", "sensor"],
                        multiple=False
                    )
                ),
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

    async def async_step_veg_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage veg room options."""
        if user_input is not None:
            new_data = {
                **self.config_entry.data,
                CONF_ROOM_NAME: user_input.get(CONF_ROOM_NAME, self.config_entry.data.get(CONF_ROOM_NAME)),
                CONF_CALENDAR_ENTITY: user_input.get(CONF_CALENDAR_ENTITY, ""),
                CONF_TODO_ENTITY: user_input.get(CONF_TODO_ENTITY, ""),
            }
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, 
                data=new_data,
                title=new_data[CONF_ROOM_NAME]
            )
            
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="veg_options",
            data_schema=vol.Schema({
                vol.Required(
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
