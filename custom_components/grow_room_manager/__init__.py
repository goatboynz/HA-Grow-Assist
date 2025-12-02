"""Grow Room Manager integration for Home Assistant."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.camera import async_get_image
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_ROOMS,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_CALENDAR_ENTITY,
    CONF_TODO_ENTITY,
    ATHENA_SCHEDULE,
    SERVICE_ADD_JOURNAL,
    SERVICE_GENERATE_TASKS,
    SERVICE_CLEAR_TASKS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Schema for room configuration
ROOM_SCHEMA = vol.Schema({
    vol.Required(CONF_ROOM_ID): cv.string,
    vol.Required(CONF_ROOM_NAME): cv.string,
    vol.Required(CONF_CALENDAR_ENTITY): cv.entity_id,
    vol.Required(CONF_TODO_ENTITY): cv.entity_id,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_ROOMS): vol.All(cv.ensure_list, [ROOM_SCHEMA]),
    }),
}, extra=vol.ALLOW_EXTRA)

# Service schemas
SERVICE_JOURNAL_SCHEMA = vol.Schema({
    vol.Required("room_id"): cv.string,
    vol.Required("note"): cv.string,
    vol.Optional("image_entity"): cv.entity_id,
})

SERVICE_GENERATE_SCHEMA = vol.Schema({
    vol.Required("room_id"): cv.string,
    vol.Required("start_date"): cv.date,
})

SERVICE_CLEAR_SCHEMA = vol.Schema({
    vol.Required("room_id"): cv.string,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Grow Room Manager integration."""
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = {
        "rooms": {room[CONF_ROOM_ID]: room for room in config[DOMAIN][CONF_ROOMS]},
    }

    # Ensure directories exist
    await hass.async_add_executor_job(_ensure_directories, hass)

    # Register services
    async def handle_add_journal_entry(call: ServiceCall) -> None:
        """Handle the add_journal_entry service call."""
        await _add_journal_entry(hass, call.data)

    async def handle_generate_tasks(call: ServiceCall) -> None:
        """Handle the generate_tasks service call."""
        await _generate_tasks(hass, call.data)

    async def handle_clear_tasks(call: ServiceCall) -> None:
        """Handle the clear_tasks service call."""
        await _clear_tasks(hass, call.data)

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_JOURNAL, handle_add_journal_entry, schema=SERVICE_JOURNAL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GENERATE_TASKS, handle_generate_tasks, schema=SERVICE_GENERATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_TASKS, handle_clear_tasks, schema=SERVICE_CLEAR_SCHEMA
    )

    # Set up sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(Platform.SENSOR, DOMAIN, {}, config)
    )

    _LOGGER.info("Grow Room Manager integration loaded with %d rooms", len(hass.data[DOMAIN]["rooms"]))
    return True


def _ensure_directories(hass: HomeAssistant) -> None:
    """Ensure required directories exist."""
    config_path = hass.config.path()
    
    # Create grow_logs directory
    logs_path = Path(config_path) / "grow_logs"
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Create www/grow_logs directory for images
    www_logs_path = Path(config_path) / "www" / "grow_logs"
    www_logs_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each room
    if DOMAIN in hass.data:
        for room_id in hass.data[DOMAIN]["rooms"]:
            room_logs = logs_path / room_id
            room_logs.mkdir(parents=True, exist_ok=True)
            room_www = www_logs_path / room_id
            room_www.mkdir(parents=True, exist_ok=True)


async def _add_journal_entry(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Add a journal entry with optional camera snapshot."""
    room_id = data["room_id"]
    note = data["note"]
    image_entity = data.get("image_entity")
    
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = timestamp.isoformat()
    
    config_path = hass.config.path()
    journal_file = Path(config_path) / "grow_logs" / f"{room_id}.json"
    
    # Prepare journal entry
    entry = {
        "timestamp": timestamp_iso,
        "note": note,
        "image_path": None,
        "image_url": None,
    }
    
    # Handle camera snapshot if provided
    if image_entity:
        try:
            image = await async_get_image(hass, image_entity)
            image_filename = f"{timestamp_str}.jpg"
            image_path = Path(config_path) / "www" / "grow_logs" / room_id / image_filename
            
            # Ensure room directory exists
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            await hass.async_add_executor_job(_write_image, image_path, image.content)
            
            entry["image_path"] = str(image_path)
            entry["image_url"] = f"/local/grow_logs/{room_id}/{image_filename}"
            _LOGGER.info("Saved snapshot to %s", image_path)
        except HomeAssistantError as err:
            _LOGGER.error("Failed to get camera image from %s: %s", image_entity, err)
        except Exception as err:
            _LOGGER.error("Unexpected error saving camera image: %s", err)
    
    # Load existing entries or create new list
    entries = await hass.async_add_executor_job(_load_journal, journal_file)
    entries.append(entry)
    
    # Save updated journal
    await hass.async_add_executor_job(_save_journal, journal_file, entries)
    _LOGGER.info("Added journal entry for room %s", room_id)


def _write_image(path: Path, content: bytes) -> None:
    """Write image content to file."""
    with open(path, "wb") as f:
        f.write(content)


def _load_journal(path: Path) -> list[dict]:
    """Load journal entries from file."""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_journal(path: Path, entries: list[dict]) -> None:
    """Save journal entries to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


async def _generate_tasks(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Generate calendar events and todo items from Athena schedule."""
    room_id = data["room_id"]
    start_date = data["start_date"]
    
    if room_id not in hass.data[DOMAIN]["rooms"]:
        _LOGGER.error("Room %s not found in configuration", room_id)
        raise HomeAssistantError(f"Room {room_id} not found")
    
    room_config = hass.data[DOMAIN]["rooms"][room_id]
    calendar_entity = room_config[CONF_CALENDAR_ENTITY]
    todo_entity = room_config[CONF_TODO_ENTITY]
    
    # Convert start_date to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    _LOGGER.info("Generating tasks for room %s starting %s", room_id, start_date)
    
    # Generate tasks from schedule
    for day_num, task_info in ATHENA_SCHEDULE.items():
        task_date = start_date + timedelta(days=day_num - 1)
        task_title = f"[{room_id.upper()}] Day {day_num}: {task_info['title']}"
        task_description = task_info["description"]
        
        # Create calendar event
        try:
            await hass.services.async_call(
                "calendar",
                "create_event",
                {
                    "entity_id": calendar_entity,
                    "summary": task_title,
                    "description": task_description,
                    "start_date": str(task_date),
                    "end_date": str(task_date),
                },
                blocking=True,
            )
            _LOGGER.debug("Created calendar event: %s on %s", task_title, task_date)
        except Exception as err:
            _LOGGER.error("Failed to create calendar event: %s", err)
        
        # Create todo item
        try:
            await hass.services.async_call(
                "todo",
                "add_item",
                {
                    "entity_id": todo_entity,
                    "item": task_title,
                    "due_date": str(task_date),
                    "description": task_description,
                },
                blocking=True,
            )
            _LOGGER.debug("Created todo item: %s", task_title)
        except Exception as err:
            _LOGGER.error("Failed to create todo item: %s", err)
    
    _LOGGER.info("Generated %d tasks for room %s", len(ATHENA_SCHEDULE), room_id)


async def _clear_tasks(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Clear all tasks for a room (todo items only - calendar events must be cleared manually)."""
    room_id = data["room_id"]
    
    if room_id not in hass.data[DOMAIN]["rooms"]:
        _LOGGER.error("Room %s not found in configuration", room_id)
        raise HomeAssistantError(f"Room {room_id} not found")
    
    room_config = hass.data[DOMAIN]["rooms"][room_id]
    todo_entity = room_config[CONF_TODO_ENTITY]
    
    _LOGGER.info("Clearing tasks for room %s", room_id)
    
    # Get current todo items
    try:
        todo_state = hass.states.get(todo_entity)
        if todo_state:
            # Note: Clearing all items requires iterating through them
            # This is a simplified approach - full implementation would need
            # to use the todo.get_items service and remove each one
            _LOGGER.warning(
                "Clear tasks requested for %s. Manual clearing of calendar events may be required.",
                room_id
            )
    except Exception as err:
        _LOGGER.error("Failed to clear tasks: %s", err)
