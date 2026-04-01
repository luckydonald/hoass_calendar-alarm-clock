"""Binary sensor platform for Calendar backed Alarm Clock."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .alarm.entries import async_setup_entry_binary_sensors
from .alarm_manager import AlarmManager
from .const import DOMAIN, LOG_NAME

_LOGGER = logging.getLogger(LOG_NAME)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Calendar backed Alarm Clock binary sensors."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not entry_data or "manager" not in entry_data:
        _LOGGER.debug("No manager found for entry %s, skipping binary sensor setup", entry.entry_id)
        return

    manager: AlarmManager = entry_data["manager"]
    await async_setup_entry_binary_sensors(hass, entry, async_add_entities, manager)
