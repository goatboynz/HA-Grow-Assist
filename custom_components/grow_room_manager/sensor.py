"""Sensor platform for Grow Room Manager."""
from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    PHASE_STRETCH,
    PHASE_BULK,
    PHASE_FINISH,
    EC_STRETCH,
    EC_BULK,
    EC_FINISH,
    DRYBACK_STRETCH,
    DRYBACK_BULK,
    DRYBACK_FINISH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Grow Room Manager sensors."""
    if DOMAIN not in hass.data:
        return

    sensors = []
    for room_id, room_config in hass.data[DOMAIN]["rooms"].items():
        sensors.append(GrowRoomStatusSensor(hass, room_id, room_config))
    
    async_add_entities(sensors, True)
    _LOGGER.info("Added %d grow room sensors", len(sensors))


class GrowRoomStatusSensor(SensorEntity):
    """Sensor representing the grow status of a room."""

    def __init__(self, hass: HomeAssistant, room_id: str, room_config: dict) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._room_id = room_id
        self._room_name = room_config[CONF_ROOM_NAME]
        self._attr_name = f"{self._room_name} Grow Status"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_grow_status"
        self._start_date: date | None = None
        self._current_day: int | None = None
        self._phase: str = STATE_UNKNOWN
        self._recommended_ec: float | None = None
        self._target_dryback: str | None = None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._current_day is not None:
            return f"Day {self._current_day}"
        return STATE_UNKNOWN

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "room_id": self._room_id,
            "room_name": self._room_name,
            "start_date": str(self._start_date) if self._start_date else None,
            "current_day": self._current_day,
            "phase": self._phase,
            "recommended_ec": self._recommended_ec,
            "target_dryback": self._target_dryback,
            "days_remaining": self._calculate_days_remaining(),
            "harvest_window": self._is_harvest_window(),
        }

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
        if self._current_day is not None:
            remaining = 77 - self._current_day
            return max(0, remaining)
        return None

    def _is_harvest_window(self) -> bool:
        """Check if we're in the harvest window (Day 77-84)."""
        if self._current_day is not None:
            return 77 <= self._current_day <= 84
        return False

    def set_start_date(self, start_date: date) -> None:
        """Set the start date and recalculate status."""
        self._start_date = start_date
        self._update_status()

    def _update_status(self) -> None:
        """Update the sensor status based on start date."""
        if self._start_date is None:
            self._current_day = None
            self._phase = STATE_UNKNOWN
            self._recommended_ec = None
            self._target_dryback = None
            return

        today = date.today()
        delta = today - self._start_date
        self._current_day = delta.days + 1  # Day 1 is the start date

        if self._current_day < 1:
            # Start date is in the future
            self._current_day = None
            self._phase = "Not Started"
            self._recommended_ec = None
            self._target_dryback = None
        else:
            self._phase, self._recommended_ec, self._target_dryback = self._calculate_phase(
                self._current_day
            )

    async def async_update(self) -> None:
        """Update the sensor."""
        # Check for input_datetime entity for this room
        start_date_entity = f"input_datetime.{self._room_id}_start_date"
        state = self.hass.states.get(start_date_entity)
        
        if state and state.state not in (STATE_UNKNOWN, "unavailable", "unknown"):
            try:
                # Parse the date from input_datetime
                date_str = state.state
                if "T" in date_str:
                    date_str = date_str.split("T")[0]
                self._start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except (ValueError, AttributeError) as err:
                _LOGGER.debug("Could not parse start date from %s: %s", start_date_entity, err)
                self._start_date = None
        
        self._update_status()
