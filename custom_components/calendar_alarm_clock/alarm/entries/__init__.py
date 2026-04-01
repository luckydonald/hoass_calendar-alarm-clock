"""Per-calendar-event binary sensor entities for Calendar backed Alarm Clock.

Each calendar event that represents an alarm gets its own device with a
``.ringing`` binary sensor:

* ``is_on`` – ``True`` while the alarm state is ``ringing`` or ``ringing_snooze``
* extra attribute ``alarm_state`` carries the full state string
  (``before`` / ``ringing`` / ``snoozed`` / ``dismissed`` / ``timed_out``)

Device ID-SUFFIX pattern: ``{DOMAIN}.{calendar_suffix}.entry.{event_id}``
Entity unique-ID pattern:  ``{DOMAIN}.{calendar_suffix}.entry.{event_id}.ringing``
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ...alarm_manager import AlarmManager
from ...const import (
    ATTR_ALARM_ID,
    ATTR_ENABLED,
    ATTR_MAX_SNOOZES,
    ATTR_NAME,
    ATTR_NEXT_SNOOZE_TIME,
    ATTR_REPEAT,
    ATTR_SNOOZE_COUNT,
    ATTR_TIME,
    ATTR_TIMEOUT,
    CONF_CALENDAR_ENTITY,
    DOMAIN,
    LOG_NAME,
)
from ...models import Alarm

_LOGGER = logging.getLogger(LOG_NAME)


def _calendar_suffix(calendar_entity: str) -> str:
    """Return the trailing component of a calendar entity id."""
    return calendar_entity.split(".")[-1]


class AlarmEntryBinarySensor(BinarySensorEntity):
    """Binary sensor for a single calendar alarm event.

    ``is_on`` reflects whether the alarm is currently ringing.
    The full alarm state is exposed as the ``alarm_state`` extra attribute.
    """

    _attr_device_class = None
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        manager: AlarmManager,
        entry: ConfigEntry,
        alarm: Alarm,
    ) -> None:
        """Initialise the alarm entry binary sensor."""
        self._manager = manager
        self._entry = entry
        self._alarm = alarm
        self._available = True

        calendar_entity: str = entry.data[CONF_CALENDAR_ENTITY]
        self._calendar_suffix = _calendar_suffix(calendar_entity)

        self._attr_unique_id = f"{DOMAIN}.{self._calendar_suffix}.entry.{alarm.id}.ringing"
        self._attr_name = "Ringing"

    # ------------------------------------------------------------------
    # BinarySensorEntity interface
    # ------------------------------------------------------------------

    @property
    def is_on(self) -> bool:
        """Return True when the alarm is actively ringing."""
        return self._alarm.state in ("ringing", "ringing_snooze")

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_ALARM_ID: self._alarm.id,
            ATTR_NAME: self._alarm.name,
            ATTR_TIME: self._alarm.time.isoformat() if self._alarm.time else None,
            ATTR_ENABLED: self._alarm.enabled,
            ATTR_REPEAT: self._alarm.repeat,
            ATTR_NEXT_SNOOZE_TIME: (
                self._alarm.next_snooze_time.isoformat() if self._alarm.next_snooze_time else None
            ),
            ATTR_SNOOZE_COUNT: self._alarm.snooze_count,
            ATTR_TIMEOUT: self._alarm.timeout,
            ATTR_MAX_SNOOZES: self._alarm.max_snoozes,
            "alarm_state": self._alarm.state,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info grouping this entity under its own alarm device."""
        alarm_time_str = self._alarm.time.strftime("%Y-%m-%d") if self._alarm.time else "unknown"
        return DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}.{self._calendar_suffix}.entry.{self._alarm.id}")},
            name=f"{self._alarm.name} ({alarm_time_str})",
            manufacturer="Calendar backed Alarm Clock",
            model="Alarm Entry",
            via_device=(DOMAIN, f"{DOMAIN}.{self._calendar_suffix}.overview"),
        )

    # ------------------------------------------------------------------
    # Update helpers called by the platform listener
    # ------------------------------------------------------------------

    @callback
    def async_update_from_alarm(self, alarm: Alarm) -> None:
        """Refresh entity state from an updated alarm."""
        self._alarm = alarm
        self._available = True
        self.async_write_ha_state()

    @callback
    def async_set_unavailable(self) -> None:
        """Mark this entity unavailable (alarm removed from calendar)."""
        self._available = False
        self.async_write_ha_state()


async def async_setup_entry_binary_sensors(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    manager: AlarmManager,
) -> None:
    """Set up AlarmEntryBinarySensor instances and keep them in sync."""
    entities: dict[str, AlarmEntryBinarySensor] = {}

    @callback
    def _on_manager_update() -> None:
        current_ids: set[str] = set(manager.alarms.keys())
        existing_ids: set[str] = set(entities.keys())

        new_ids = current_ids - existing_ids
        if new_ids:
            new_entities: list[AlarmEntryBinarySensor] = []
            for alarm_id in new_ids:
                sensor = AlarmEntryBinarySensor(manager, entry, manager.alarms[alarm_id])
                entities[alarm_id] = sensor
                new_entities.append(sensor)
            async_add_entities(new_entities)

        for alarm_id in current_ids & existing_ids:
            entities[alarm_id].async_update_from_alarm(manager.alarms[alarm_id])

        for alarm_id in existing_ids - current_ids:
            entities[alarm_id].async_set_unavailable()

    # Initial population
    _on_manager_update()

    manager.add_listener(_on_manager_update)
