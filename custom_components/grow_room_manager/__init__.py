"""Grow Room Manager integration for Home Assistant."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_ROOMS,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_CALENDAR_ENTITY,
    CONF_TODO_ENTITY,
    CONF_START_DATE,
    ATHENA_SCHEDULE,
    SERVICE_ADD_JOURNAL,
    SERVICE_GENERATE_TASKS,
    SERVICE_CLEAR_TASKS,
    SERVICE_EXPORT_JOURNAL,
    SERVICE_SET_START_DATE,
    SERVICE_GET_TODAY_TASKS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Grow Room Manager integration."""
    hass.data.setdefault(DOMAIN, {"rooms": {}})
    
    # Register services immediately so they're available even without config entries
    await _async_register_services(hass)
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grow Room Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {"rooms": {}})
    
    # Store room config from entry
    room_id = entry.data[CONF_ROOM_ID]
    hass.data[DOMAIN]["rooms"][room_id] = dict(entry.data)

    # Ensure directories exist
    await hass.async_add_executor_job(_ensure_directories, hass, room_id)
    
    # Register services (only once)
    await _async_register_services(hass)
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Grow Room Manager: Room '%s' loaded", room_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    room_id = entry.data[CONF_ROOM_ID]
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN]["rooms"].pop(room_id, None)
        _LOGGER.info("Grow Room Manager: Room '%s' unloaded", room_id)
    
    return unload_ok


def _ensure_directories(hass: HomeAssistant, room_id: str) -> None:
    """Ensure required directories exist."""
    config_path = hass.config.path()
    
    # Create grow_logs directory
    logs_path = Path(config_path) / "grow_logs"
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Create www/grow_logs directory for images
    www_logs_path = Path(config_path) / "www" / "grow_logs"
    www_logs_path.mkdir(parents=True, exist_ok=True)
    
    # Create room subdirectories
    room_logs = logs_path / room_id
    room_logs.mkdir(parents=True, exist_ok=True)
    room_www = www_logs_path / room_id
    room_www.mkdir(parents=True, exist_ok=True)


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register services for the integration."""
    
    # Only register once
    if hass.services.has_service(DOMAIN, SERVICE_GENERATE_TASKS):
        return
    
    # Service schemas
    service_journal_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
        vol.Required("note"): cv.string,
        vol.Optional("image_entity"): cv.entity_id,
    })
    
    service_generate_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
        vol.Required("start_date"): cv.date,
        vol.Optional("calendar_entity"): cv.entity_id,
        vol.Optional("todo_entity"): cv.entity_id,
    })
    
    service_clear_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
    })
    
    service_export_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
        vol.Optional("format", default="csv"): vol.In(["csv", "json"]),
    })
    
    service_set_start_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
        vol.Required("start_date"): cv.date,
    })
    
    service_today_tasks_schema = vol.Schema({
        vol.Required("room_id"): cv.string,
    })

    async def handle_add_journal_entry(call: ServiceCall) -> None:
        """Handle the add_journal_entry service call."""
        await _add_journal_entry(hass, call.data)

    async def handle_generate_tasks(call: ServiceCall) -> None:
        """Handle the generate_tasks service call."""
        await _generate_tasks(hass, call.data)

    async def handle_clear_tasks(call: ServiceCall) -> None:
        """Handle the clear_tasks service call."""
        await _clear_tasks(hass, call.data)

    async def handle_export_journal(call: ServiceCall) -> None:
        """Handle the export_journal service call."""
        await _export_journal(hass, call.data)

    async def handle_set_start_date(call: ServiceCall) -> None:
        """Handle the set_start_date service call."""
        await _set_start_date(hass, call.data)

    async def handle_get_today_tasks(call: ServiceCall) -> None:
        """Handle the get_today_tasks service call."""
        await _get_today_tasks(hass, call.data)

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_JOURNAL, handle_add_journal_entry, schema=service_journal_schema
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GENERATE_TASKS, handle_generate_tasks, schema=service_generate_schema
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_TASKS, handle_clear_tasks, schema=service_clear_schema
    )
    hass.services.async_register(
        DOMAIN, SERVICE_EXPORT_JOURNAL, handle_export_journal, schema=service_export_schema
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_START_DATE, handle_set_start_date, schema=service_set_start_schema
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_TODAY_TASKS, handle_get_today_tasks, schema=service_today_tasks_schema
    )
    
    _LOGGER.info("Grow Room Manager services registered")


async def _add_journal_entry(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Add a journal entry with optional camera snapshot."""
    room_id = data["room_id"]
    note = data["note"]
    image_entity = data.get("image_entity")
    
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = timestamp.isoformat()
    
    config_path = hass.config.path()
    
    # Ensure directory exists
    journal_dir = Path(config_path) / "grow_logs"
    journal_dir.mkdir(parents=True, exist_ok=True)
    
    journal_file = journal_dir / f"{room_id}.json"
    
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
            from homeassistant.components.camera import async_get_image
            image = await async_get_image(hass, image_entity)
            image_filename = f"{timestamp_str}.jpg"
            image_dir = Path(config_path) / "www" / "grow_logs" / room_id
            image_dir.mkdir(parents=True, exist_ok=True)
            image_path = image_dir / image_filename
            
            # Save image
            await hass.async_add_executor_job(_write_image, image_path, image.content)
            
            entry["image_path"] = str(image_path)
            entry["image_url"] = f"/local/grow_logs/{room_id}/{image_filename}"
            _LOGGER.info("Saved snapshot to %s", image_path)
        except Exception as err:
            _LOGGER.error("Failed to get camera image from %s: %s", image_entity, err)
    
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
    
    # Get entities from service call or from stored room config
    calendar_entity = data.get("calendar_entity")
    todo_entity = data.get("todo_entity")
    
    # Fall back to stored config if not provided in service call
    if room_id in hass.data[DOMAIN]["rooms"]:
        room_config = hass.data[DOMAIN]["rooms"][room_id]
        if not calendar_entity:
            calendar_entity = room_config.get(CONF_CALENDAR_ENTITY)
        if not todo_entity:
            todo_entity = room_config.get(CONF_TODO_ENTITY)
    
    if not calendar_entity and not todo_entity:
        raise HomeAssistantError(
            f"No calendar or todo entity configured for room {room_id}. "
            "Please provide calendar_entity and/or todo_entity in the service call."
        )
    
    # Convert start_date to date if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    _LOGGER.info("Generating tasks for room %s starting %s", room_id, start_date)
    
    tasks_created = 0
    
    # Generate tasks from schedule
    for day_num, task_info in ATHENA_SCHEDULE.items():
        task_date = start_date + timedelta(days=day_num - 1)
        task_title = f"[{room_id.upper()}] Day {day_num}: {task_info['title']}"
        task_description = task_info["description"]
        
        # Create calendar event
        if calendar_entity:
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
        if todo_entity:
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
        
        tasks_created += 1
    
    _LOGGER.info("Generated %d tasks for room %s", tasks_created, room_id)


async def _clear_tasks(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Clear all tasks for a room."""
    room_id = data["room_id"]
    _LOGGER.info("Clear tasks requested for room %s", room_id)
    _LOGGER.warning(
        "Automatic task clearing is not fully supported. "
        "Please manually clear calendar events and todo items for room %s.",
        room_id
    )


async def _export_journal(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Export journal entries to CSV or JSON file."""
    import csv
    
    room_id = data["room_id"]
    export_format = data.get("format", "csv")
    
    config_path = hass.config.path()
    journal_file = Path(config_path) / "grow_logs" / f"{room_id}.json"
    
    if not journal_file.exists():
        raise HomeAssistantError(f"No journal found for room {room_id}")
    
    entries = await hass.async_add_executor_job(_load_journal, journal_file)
    
    if not entries:
        raise HomeAssistantError(f"Journal for room {room_id} is empty")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if export_format == "csv":
        export_file = Path(config_path) / "www" / "grow_logs" / f"{room_id}_export_{timestamp}.csv"
        
        def write_csv():
            export_file.parent.mkdir(parents=True, exist_ok=True)
            with open(export_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "note", "image_url"])
                writer.writeheader()
                for entry in entries:
                    writer.writerow({
                        "timestamp": entry.get("timestamp", ""),
                        "note": entry.get("note", ""),
                        "image_url": entry.get("image_url", ""),
                    })
        
        await hass.async_add_executor_job(write_csv)
        _LOGGER.info("Exported journal to %s", export_file)
    else:
        export_file = Path(config_path) / "www" / "grow_logs" / f"{room_id}_export_{timestamp}.json"
        
        def write_json():
            export_file.parent.mkdir(parents=True, exist_ok=True)
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
        
        await hass.async_add_executor_job(write_json)
        _LOGGER.info("Exported journal to %s", export_file)


async def _set_start_date(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Set the start date for a room by updating its config entry."""
    from datetime import date
    
    room_id = data["room_id"]
    start_date = data["start_date"]
    
    # Convert to string if date object
    if isinstance(start_date, date):
        start_date = start_date.isoformat()
    
    # Find the config entry for this room
    entry_found = False
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_ROOM_ID) == room_id:
            # Update the config entry with new start date
            new_data = {**entry.data, CONF_START_DATE: start_date}
            hass.config_entries.async_update_entry(entry, data=new_data)
            
            # Also update the in-memory data
            if room_id in hass.data[DOMAIN]["rooms"]:
                hass.data[DOMAIN]["rooms"][room_id][CONF_START_DATE] = start_date
            
            # Reload to update sensors
            await hass.config_entries.async_reload(entry.entry_id)
            
            _LOGGER.info("Set start date for %s to %s", room_id, start_date)
            entry_found = True
            break
    
    if not entry_found:
        raise HomeAssistantError(
            f"Room {room_id} not found. Add it via Settings > Devices & Services > Grow Room Manager."
        )


async def _get_today_tasks(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Get tasks for today and fire an event with the details."""
    from datetime import date
    
    room_id = data["room_id"]
    start_date = None
    
    # Get start date from config entry
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_ROOM_ID) == room_id:
            start_date_str = entry.data.get(CONF_START_DATE)
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            break
    
    if not start_date:
        raise HomeAssistantError(
            f"No start date set for room {room_id}. "
            "Set it via Settings > Devices & Services > Grow Room Manager > Configure."
        )
    
    # Calculate current day
    current_day = (date.today() - start_date).days + 1
    
    if current_day < 1:
        _LOGGER.info("Grow cycle for %s hasn't started yet", room_id)
        return
    
    # Check if there's a task for today
    if current_day in ATHENA_SCHEDULE:
        task = ATHENA_SCHEDULE[current_day]
        
        # Fire an event that automations can listen to
        hass.bus.async_fire(
            f"{DOMAIN}_task_today",
            {
                "room_id": room_id,
                "day": current_day,
                "title": task["title"],
                "description": task["description"],
                "category": task.get("category", ""),
                "priority": task.get("priority", "medium"),
                "phase": task.get("phase", ""),
            }
        )
        _LOGGER.info("Task for %s Day %d: %s", room_id, current_day, task["title"])
    else:
        _LOGGER.debug("No scheduled task for %s on Day %d", room_id, current_day)
