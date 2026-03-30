"""Overview sensor entities for Calendar backed Alarm Clock.

These entities are grouped under an "Overview" device per calendar integration
and provide summarising views of the alarm set:

- OverviewNameSensor  – ENUM sensor exposing the name of the previous / current
                        / next alarm (ID-SUFFIX: .overview.<role>.name)
- TodayCountSensor    – MEASUREMENT sensor counting alarms on today's date,
                        split into total / upcoming / past variants
                        (ID-SUFFIX: .overview.today.<role>)
"""

from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from ...alarm_manager import AlarmManager
from ...const import CONF_CALENDAR_ENTITY, DOMAIN, LOG_NAME
from ...models import Alarm

_LOGGER = logging.getLogger(LOG_NAME)

OverviewRole = Literal["previous", "current", "next"]
TodayRole = Literal["total", "upcoming", "past"]


def _calendar_suffix(calendar_entity: str) -> str:
    """Return the trailing component of a calendar entity id.

    Example: ``'calendar.my_calendar'`` → ``'my_calendar'``.
    """
    return calendar_entity.split(".")[-1]


def _overview_device(calendar_entity: str) -> DeviceInfo:
    """DeviceInfo for the Overview device of a given calendar."""
    suffix = _calendar_suffix(calendar_entity)
    return DeviceInfo(
        identifiers={(DOMAIN, f"{DOMAIN}.{suffix}.overview")},
        name="Overview",
        manufacturer="Calendar backed Alarm Clock",
        model="Overview",
    )


class OverviewNameSensor(SensorEntity):
    """ENUM sensor exposing the name of the previous, current, or next alarm.

    Unique ID pattern: ``{DOMAIN}.{calendar_suffix}.overview.{role}.name``
    """

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_state_class = None
    _attr_last_reset = None
    _attr_suggested_display_precision = None
    _attr_suggested_unit_of_measurement = None
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        manager: AlarmManager,
        entry: ConfigEntry,
        role: OverviewRole,
    ) -> None:
        """Initialise the overview name sensor."""
        self._manager = manager
        self._entry = entry
        self._role: OverviewRole = role

        calendar_entity: str = entry.data[CONF_CALENDAR_ENTITY]
        suffix = _calendar_suffix(calendar_entity)
        self._attr_unique_id = f"{DOMAIN}.{suffix}.overview.{role}.name"
        self._attr_name = f"{role.capitalize()} Alarm Name"
        self._attr_device_info = _overview_device(calendar_entity)

    # ------------------------------------------------------------------
    # SensorEntity interface
    # ------------------------------------------------------------------

    @property
    def options(self) -> list[str]:
        """Return the list of valid alarm names (used by SensorDeviceClass.ENUM)."""
        return [a.name for a in self._manager.alarms.values()]

    @property
    def native_value(self) -> str | None:
        """Return the name of the relevant alarm, or None."""
        alarm = self._relevant_alarm()
        return alarm.name if alarm else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _relevant_alarm(self) -> Alarm | None:
        if self._role == "next":
            return self._manager.next_alarm
        if self._role == "previous":
            return self._manager.previous_alarm
        # "current" – the first ringing alarm
        for alarm in self._manager.alarms.values():
            if alarm.state in ("ringing", "ringing_snooze"):
                return alarm
        return None

    @callback
    def async_refresh(self) -> None:
        """Called by the sensor platform when the manager emits an update."""
        self.async_write_ha_state()


class TodayCountSensor(SensorEntity):
    """MEASUREMENT sensor counting alarms on today's date.

    Three roles:

    * ``total``    – all alarms (past + current + future) on today's date
    * ``upcoming`` – alarms whose time is still in the future today
    * ``past``     – alarms whose time has already passed today

    Unique ID pattern: ``{DOMAIN}.{calendar_suffix}.overview.today.{role}``
    """

    _attr_device_class = None
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_last_reset = None
    _attr_options = None
    _attr_suggested_display_precision = 0
    _attr_suggested_unit_of_measurement = None
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = None  # Unit provided via translations ("alarms")

    def __init__(
        self,
        manager: AlarmManager,
        entry: ConfigEntry,
        role: TodayRole,
    ) -> None:
        """Initialise the today-count sensor."""
        self._manager = manager
        self._entry = entry
        self._role: TodayRole = role

        calendar_entity: str = entry.data[CONF_CALENDAR_ENTITY]
        suffix = _calendar_suffix(calendar_entity)
        self._attr_unique_id = f"{DOMAIN}.{suffix}.overview.today.{role}"
        self._attr_name = f"Today {role.capitalize()} Alarms"
        self._attr_device_info = _overview_device(calendar_entity)

    @property
    def native_value(self) -> int:
        """Return the count of today's alarms matching this sensor's role."""
        now = dt_util.now()
        today = now.date()
        alarms = [a for a in self._manager.alarms.values() if a.time and a.time.date() == today]

        if self._role == "total":
            return len(alarms)
        if self._role == "upcoming":
            return sum(1 for a in alarms if a.time > now)
        # "past"
        return sum(1 for a in alarms if a.time <= now)

    @callback
    def async_refresh(self) -> None:
        """Called by the sensor platform when the manager emits an update."""
        self.async_write_ha_state()


def build_overview_entities(
    manager: AlarmManager,
    entry: ConfigEntry,
) -> list[SensorEntity]:
    """Return all overview sensor entities for a calendar config entry."""
    entities: list[SensorEntity] = []

    for role in ("previous", "current", "next"):
        entities.append(OverviewNameSensor(manager, entry, role))  # type: ignore[arg-type]

    for role in ("total", "upcoming", "past"):
        entities.append(TodayCountSensor(manager, entry, role))  # type: ignore[arg-type]

    return entities


async def async_setup_overview_sensors(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    manager: AlarmManager,
) -> None:
    """Set up the overview sensor entities and wire them to the manager."""
    entities = build_overview_entities(manager, entry)
    async_add_entities(entities)

    refreshable = [e for e in entities if isinstance(e, (OverviewNameSensor, TodayCountSensor))]

    @callback
    def _on_manager_update() -> None:
        for entity in refreshable:
            entity.async_refresh()

    manager.add_listener(_on_manager_update)
