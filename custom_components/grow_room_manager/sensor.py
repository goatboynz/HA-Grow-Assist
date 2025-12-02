"""Sensor platform for Grow Room Manager."""
from __future__ import annotations

import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_START_DATE,
    CONF_START_DATE_ENTITY,
    CONF_ROOM_TYPE,
    ROOM_TYPE_FLOWER,
    ROOM_TYPE_VEG,
    PHASE_STRETCH,
    PHASE_BULK,
    PHASE_FINISH,
    PHASE_CLONE,
    PHASE_PREVEG,
    PHASE_EARLY_VEG,
    PHASE_LATE_VEG,
    PHASE_MOTHER,
    EC_STRETCH,
    EC_BULK,
    EC_FINISH,
    EC_CLONE,
    EC_PREVEG,
    EC_EARLY_VEG,
    EC_LATE_VEG,
    EC_MOTHER,
    DRYBACK_STRETCH,
    DRYBACK_BULK,
    DRYBACK_FINISH,
    VEG_STAGE_DURATIONS,
    ATHENA_SCHEDULE,
    VEG_SCHEDULE,
    ATHENA_FEED_CHART,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grow Room Manager sensors from a config entry."""
    room_id = entry.data[CONF_ROOM_ID]
    room_name = entry.data[CONF_ROOM_NAME]
    room_type = entry.data.get(CONF_ROOM_TYPE, ROOM_TYPE_FLOWER)
    
    if room_type == ROOM_TYPE_VEG:
        # Veg room sensors
        sensors = [
            VegRoomStatusSensor(hass, room_id, room_name, entry),
            VegRoomBatchCountSensor(hass, room_id, room_name, entry),
            VegRoomNextTaskSensor(hass, room_id, room_name, entry),
            GrowRoomJournalCountSensor(hass, room_id, room_name, entry),
        ]
    else:
        # Flower room sensors
        sensors = [
            GrowRoomStatusSensor(hass, room_id, room_name, entry),
            GrowRoomProgressSensor(hass, room_id, room_name, entry),
            GrowRoomNextTaskSensor(hass, room_id, room_name, entry),
            GrowRoomJournalCountSensor(hass, room_id, room_name, entry),
        ]
    
    async_add_entities(sensors, True)
    _LOGGER.info("Added %d %s room sensors for %s", len(sensors), room_type, room_id)


class GrowRoomBaseSensor(SensorEntity):
    """Base class for grow room sensors."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        room_id: str, 
        room_name: str,
        entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._room_id = room_id
        self._room_name = room_name
        self._entry = entry
        self._start_date: date | None = None

    def _get_start_date(self) -> date | None:
        """Get the start date from config entry or entity."""
        # First check if there's a start date entity configured
        start_date_entity = self._entry.data.get(CONF_START_DATE_ENTITY)
        
        if start_date_entity:
            state = self.hass.states.get(start_date_entity)
            if state and state.state not in (STATE_UNKNOWN, "unavailable", "unknown", None, ""):
                try:
                    date_str = state.state
                    if "T" in date_str:
                        date_str = date_str.split("T")[0]
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except (ValueError, AttributeError):
                    _LOGGER.debug("Could not parse date from entity %s", start_date_entity)
        
        # Fall back to static start date from config
        start_date_str = self._entry.data.get(CONF_START_DATE)
        
        if start_date_str:
            try:
                if isinstance(start_date_str, date):
                    return start_date_str
                return datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except (ValueError, AttributeError):
                pass
        return None

    def _get_current_day(self) -> int | None:
        """Calculate current day of flower."""
        if self._start_date is None:
            return None
        delta = date.today() - self._start_date
        day = delta.days + 1
        return day if day >= 1 else None


class GrowRoomStatusSensor(GrowRoomBaseSensor):
    """Sensor representing the grow status of a room."""

    def __init__(self, hass: HomeAssistant, room_id: str, room_name: str, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass, room_id, room_name, entry)
        self._attr_name = f"{room_name} Grow Status"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_grow_status"
        self._current_day: int | None = None
        self._phase: str = "Not Started"
        self._recommended_ec: float | None = None
        self._target_dryback: str | None = None
        self._week: int | None = None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._current_day is not None and self._current_day >= 1:
            return f"Day {self._current_day}"
        return "Not Started"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {
            "room_id": self._room_id,
            "room_name": self._room_name,
            "start_date": str(self._start_date) if self._start_date else None,
            "current_day": self._current_day,
            "current_week": self._week,
            "phase": self._phase,
            "recommended_ec": self._recommended_ec,
            "target_dryback": self._target_dryback,
            "days_remaining": self._calculate_days_remaining(),
            "harvest_window": self._is_harvest_window(),
            "days_in_phase": self._days_in_phase(),
            "phase_progress": self._phase_progress(),
        }
        
        # Add environmental targets based on phase
        if self._phase == PHASE_STRETCH:
            attrs["target_temp_day"] = "78-82°F (25-28°C)"
            attrs["target_temp_night"] = "68-72°F (20-22°C)"
            attrs["target_humidity"] = "55-65%"
            attrs["target_vpd"] = "1.0-1.2 kPa"
        elif self._phase == PHASE_BULK:
            attrs["target_temp_day"] = "78-82°F (25-28°C)"
            attrs["target_temp_night"] = "65-70°F (18-21°C)"
            attrs["target_humidity"] = "50-60%"
            attrs["target_vpd"] = "1.2-1.4 kPa"
        elif self._phase == PHASE_FINISH:
            attrs["target_temp_day"] = "75-78°F (24-26°C)"
            attrs["target_temp_night"] = "62-68°F (17-20°C)"
            attrs["target_humidity"] = "40-50%"
            attrs["target_vpd"] = "1.4-1.6 kPa"
        
        return attrs

    @property
    def icon(self) -> str:
        """Return the icon based on current phase."""
        if self._phase == PHASE_STRETCH:
            return "mdi:sprout"
        elif self._phase == PHASE_BULK:
            return "mdi:flower"
        elif self._phase == PHASE_FINISH:
            return "mdi:fruit-grapes"
        return "mdi:cannabis"

    def _calculate_phase(self, day: int) -> tuple[str, float, str]:
        """Calculate the current phase based on day number."""
        if day <= 21:
            return PHASE_STRETCH, EC_STRETCH, DRYBACK_STRETCH
        elif day <= 55:
            return PHASE_BULK, EC_BULK, DRYBACK_BULK
        else:
            return PHASE_FINISH, EC_FINISH, DRYBACK_FINISH

    def _calculate_days_remaining(self) -> int | None:
        """Calculate days remaining until typical harvest (Day 77)."""
        if self._current_day is not None and self._current_day >= 1:
            remaining = 77 - self._current_day
            return max(0, remaining)
        return None

    def _is_harvest_window(self) -> bool:
        """Check if we're in the harvest window (Day 77-84)."""
        if self._current_day is not None:
            return 77 <= self._current_day <= 84
        return False

    def _days_in_phase(self) -> int | None:
        """Calculate days spent in current phase."""
        if self._current_day is None:
            return None
        if self._current_day <= 21:
            return self._current_day
        elif self._current_day <= 55:
            return self._current_day - 21
        else:
            return self._current_day - 55

    def _phase_progress(self) -> str | None:
        """Calculate progress through current phase as percentage."""
        if self._current_day is None:
            return None
        if self._current_day <= 21:
            pct = min(100, int((self._current_day / 21) * 100))
        elif self._current_day <= 55:
            pct = min(100, int(((self._current_day - 21) / 34) * 100))
        else:
            pct = min(100, int(((self._current_day - 55) / 29) * 100))
        return f"{pct}%"

    async def async_update(self) -> None:
        """Update the sensor."""
        self._start_date = self._get_start_date()
        self._current_day = self._get_current_day()
        
        if self._current_day is not None and self._current_day >= 1:
            self._week = ((self._current_day - 1) // 7) + 1
            self._phase, self._recommended_ec, self._target_dryback = self._calculate_phase(
                self._current_day
            )
        else:
            self._week = None
            self._phase = "Not Started"
            self._recommended_ec = None
            self._target_dryback = None


class GrowRoomProgressSensor(GrowRoomBaseSensor):
    """Sensor showing overall grow cycle progress."""

    def __init__(self, hass: HomeAssistant, room_id: str, room_name: str, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass, room_id, room_name, entry)
        self._attr_name = f"{room_name} Grow Progress"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_grow_progress"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._progress: int = 0

    @property
    def native_value(self) -> int:
        """Return the progress percentage."""
        return self._progress

    @property
    def icon(self) -> str:
        """Return icon based on progress."""
        if self._progress >= 90:
            return "mdi:check-circle"
        elif self._progress >= 50:
            return "mdi:circle-half-full"
        elif self._progress > 0:
            return "mdi:circle-outline"
        return "mdi:circle-off-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        current_day = self._get_current_day()
        return {
            "room_id": self._room_id,
            "current_day": current_day,
            "total_days": 84,
            "estimated_harvest": str(self._start_date + timedelta(days=76)) if self._start_date else None,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        self._start_date = self._get_start_date()
        current_day = self._get_current_day()
        
        if current_day is not None and current_day >= 1:
            # Progress based on 84-day cycle
            self._progress = min(100, int((current_day / 84) * 100))
        else:
            self._progress = 0


class GrowRoomNextTaskSensor(GrowRoomBaseSensor):
    """Sensor showing the next scheduled task."""

    def __init__(self, hass: HomeAssistant, room_id: str, room_name: str, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass, room_id, room_name, entry)
        self._attr_name = f"{room_name} Next Task"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_next_task"
        self._next_task: str | None = None
        self._next_task_day: int | None = None
        self._next_task_date: date | None = None
        self._next_task_priority: str | None = None
        self._days_until: int | None = None

    @property
    def native_value(self) -> str:
        """Return the next task title."""
        return self._next_task or "No upcoming tasks"

    @property
    def icon(self) -> str:
        """Return icon based on priority."""
        if self._next_task_priority == "critical":
            return "mdi:alert-circle"
        elif self._next_task_priority == "high":
            return "mdi:alert"
        return "mdi:calendar-check"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "room_id": self._room_id,
            "task_day": self._next_task_day,
            "task_date": str(self._next_task_date) if self._next_task_date else None,
            "days_until": self._days_until,
            "priority": self._next_task_priority,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        self._start_date = self._get_start_date()
        current_day = self._get_current_day()
        
        self._next_task = None
        self._next_task_day = None
        self._next_task_date = None
        self._next_task_priority = None
        self._days_until = None
        
        if current_day is None or self._start_date is None:
            return
        
        # Find the next task
        sorted_days = sorted(ATHENA_SCHEDULE.keys())
        for task_day in sorted_days:
            if task_day >= current_day:
                task_info = ATHENA_SCHEDULE[task_day]
                self._next_task = task_info["title"]
                self._next_task_day = task_day
                self._next_task_date = self._start_date + timedelta(days=task_day - 1)
                self._next_task_priority = task_info.get("priority", "medium")
                self._days_until = task_day - current_day
                break


class GrowRoomJournalCountSensor(GrowRoomBaseSensor):
    """Sensor showing journal entry count."""

    def __init__(self, hass: HomeAssistant, room_id: str, room_name: str, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass, room_id, room_name, entry)
        self._attr_name = f"{room_name} Journal Entries"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_journal_count"
        self._attr_icon = "mdi:notebook"
        self._count: int = 0
        self._last_entry: str | None = None
        self._last_entry_date: str | None = None

    @property
    def native_value(self) -> int:
        """Return the journal entry count."""
        return self._count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "room_id": self._room_id,
            "last_entry_preview": self._last_entry[:100] + "..." if self._last_entry and len(self._last_entry) > 100 else self._last_entry,
            "last_entry_date": self._last_entry_date,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        journal_file = Path(self.hass.config.path()) / "grow_logs" / f"{self._room_id}.json"
        
        if journal_file.exists():
            try:
                data = await self.hass.async_add_executor_job(self._read_journal, journal_file)
                self._count = len(data)
                if data:
                    last = data[-1]
                    self._last_entry = last.get("note")
                    self._last_entry_date = last.get("timestamp", "")[:10]
                else:
                    self._last_entry = None
                    self._last_entry_date = None
            except Exception as err:
                _LOGGER.error("Error reading journal: %s", err)
                self._count = 0
        else:
            self._count = 0
            self._last_entry = None
            self._last_entry_date = None

    def _read_journal(self, path: Path) -> list:
        """Read journal file."""
        with open(path, "r") as f:
            return json.load(f)


class VegRoomStatusSensor(SensorEntity):
    """Sensor showing veg room status with batch summary."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        room_id: str, 
        room_name: str,
        entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._room_id = room_id
        self._room_name = room_name
        self._entry = entry
        self._attr_name = f"{room_name} Status"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_veg_status"
        self._batch_count: int = 0
        self._batches_by_stage: dict = {}
        self._total_plants: int = 0

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._batch_count == 0:
            return "Empty"
        return f"{self._batch_count} batches"

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:sprout-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {
            "room_id": self._room_id,
            "room_name": self._room_name,
            "room_type": "veg",
            "active_batches": self._batch_count,
            "total_plants": self._total_plants,
            "batches_by_stage": self._batches_by_stage,
        }
        
        # Add recommended EC based on most advanced stage
        if self._batches_by_stage:
            stages_present = list(self._batches_by_stage.keys())
            stage_order = [PHASE_CLONE, PHASE_PREVEG, PHASE_EARLY_VEG, PHASE_LATE_VEG, PHASE_MOTHER]
            most_advanced = None
            for stage in reversed(stage_order):
                if stage in stages_present:
                    most_advanced = stage
                    break
            
            if most_advanced:
                ec_map = {
                    PHASE_CLONE: EC_CLONE,
                    PHASE_PREVEG: EC_PREVEG,
                    PHASE_EARLY_VEG: EC_EARLY_VEG,
                    PHASE_LATE_VEG: EC_LATE_VEG,
                    PHASE_MOTHER: EC_MOTHER,
                }
                attrs["recommended_ec"] = ec_map.get(most_advanced, 1.5)
                attrs["most_advanced_stage"] = most_advanced
        
        # Environmental targets for veg
        attrs["target_temp_day"] = "75-82°F (24-28°C)"
        attrs["target_temp_night"] = "68-75°F (20-24°C)"
        attrs["target_humidity"] = "55-70%"
        attrs["target_vpd"] = "0.8-1.2 kPa"
        attrs["target_ph"] = "5.8-6.2"
        
        return attrs

    async def async_update(self) -> None:
        """Update the sensor."""
        batches = self.hass.data.get(DOMAIN, {}).get("veg_batches", {}).get(self._room_id, [])
        
        # Filter active batches
        active_batches = [b for b in batches if b.get("active", True)]
        self._batch_count = len(active_batches)
        
        # Count by stage
        self._batches_by_stage = {}
        self._total_plants = 0
        
        for batch in active_batches:
            stage = batch.get("stage", "Unknown")
            if stage not in self._batches_by_stage:
                self._batches_by_stage[stage] = {"count": 0, "plants": 0, "batches": []}
            self._batches_by_stage[stage]["count"] += 1
            self._batches_by_stage[stage]["plants"] += batch.get("plant_count", 0)
            self._batches_by_stage[stage]["batches"].append(batch.get("batch_name", "Unknown"))
            self._total_plants += batch.get("plant_count", 0)


class VegRoomBatchCountSensor(SensorEntity):
    """Sensor showing count of active veg batches."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        room_id: str, 
        room_name: str,
        entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._room_id = room_id
        self._room_name = room_name
        self._entry = entry
        self._attr_name = f"{room_name} Active Batches"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_batch_count"
        self._attr_icon = "mdi:package-variant"
        self._count: int = 0
        self._batches: list = []

    @property
    def native_value(self) -> int:
        """Return the batch count."""
        return self._count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "room_id": self._room_id,
            "batches": [
                {
                    "batch_id": b.get("batch_id"),  # Include batch_id for service calls
                    "name": b.get("batch_name"),
                    "stage": b.get("stage"),
                    "plants": b.get("plant_count", 0),
                    "strain": b.get("strain", ""),
                    "start_date": b.get("start_date"),
                    "destination": b.get("destination_room", ""),
                }
                for b in self._batches
            ],
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        batches = self.hass.data.get(DOMAIN, {}).get("veg_batches", {}).get(self._room_id, [])
        self._batches = [b for b in batches if b.get("active", True)]
        self._count = len(self._batches)


class VegRoomNextTaskSensor(SensorEntity):
    """Sensor showing next task across all veg batches."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        room_id: str, 
        room_name: str,
        entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._room_id = room_id
        self._room_name = room_name
        self._entry = entry
        self._attr_name = f"{room_name} Next Task"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_veg_next_task"
        self._next_task: str | None = None
        self._next_task_date: date | None = None
        self._next_task_batch: str | None = None
        self._days_until: int | None = None

    @property
    def native_value(self) -> str:
        """Return the next task title."""
        return self._next_task or "No upcoming tasks"

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:calendar-check"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "room_id": self._room_id,
            "task_date": str(self._next_task_date) if self._next_task_date else None,
            "batch_name": self._next_task_batch,
            "days_until": self._days_until,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        batches = self.hass.data.get(DOMAIN, {}).get("veg_batches", {}).get(self._room_id, [])
        active_batches = [b for b in batches if b.get("active", True)]
        
        self._next_task = None
        self._next_task_date = None
        self._next_task_batch = None
        self._days_until = None
        
        if not active_batches:
            return
        
        today = date.today()
        earliest_task = None
        earliest_date = None
        earliest_batch = None
        
        # Find the next task across all batches
        for batch in active_batches:
            batch_name = batch.get("batch_name", "Unknown")
            start_date_str = batch.get("start_date")
            stage = batch.get("stage")
            
            if not start_date_str:
                continue
            
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            # Calculate day offset based on stage
            stage_offsets = {
                PHASE_CLONE: 0,
                PHASE_PREVEG: 14,
                PHASE_EARLY_VEG: 21,
                PHASE_LATE_VEG: 35,
                PHASE_MOTHER: 0,
            }
            day_offset = stage_offsets.get(stage, 0)
            
            # Find next task for this batch
            current_day = (today - start_date).days + 1 + day_offset
            
            for task_day in sorted(VEG_SCHEDULE.keys()):
                if task_day >= current_day:
                    task_date = start_date + timedelta(days=task_day - day_offset - 1)
                    if task_date >= today:
                        if earliest_date is None or task_date < earliest_date:
                            earliest_date = task_date
                            earliest_task = VEG_SCHEDULE[task_day]["title"]
                            earliest_batch = batch_name
                        break
        
        if earliest_task:
            self._next_task = earliest_task
            self._next_task_date = earliest_date
            self._next_task_batch = earliest_batch
            self._days_until = (earliest_date - today).days if earliest_date else None
