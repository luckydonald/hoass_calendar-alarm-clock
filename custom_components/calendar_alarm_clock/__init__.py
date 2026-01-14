"""Calendar Alarm Clock integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_SNOOZE_DURATION,
    CONF_DEFAULT_ALARM_TIMEOUT,
    CONF_DEFAULT_MAX_SNOOZES,
    DEFAULT_SNOOZE_DURATION,
    DEFAULT_ALARM_TIMEOUT,
    DEFAULT_MAX_SNOOZES,
    UPDATE_INTERVAL,
)
from .alarm_manager import AlarmManager
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Calendar Alarm Clock from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    calendar_entity = entry.data[CONF_CALENDAR_ENTITY]

    # Get configuration options with defaults
    snooze_duration = entry.options.get(
        CONF_DEFAULT_SNOOZE_DURATION, DEFAULT_SNOOZE_DURATION
    )
    alarm_timeout = entry.options.get(
        CONF_DEFAULT_ALARM_TIMEOUT, DEFAULT_ALARM_TIMEOUT
    )
    max_snoozes = entry.options.get(
        CONF_DEFAULT_MAX_SNOOZES, DEFAULT_MAX_SNOOZES
    )

    # Create alarm manager
    manager = AlarmManager(
        hass=hass,
        calendar_entity=calendar_entity,
        default_snooze_duration=snooze_duration,
        default_alarm_timeout=alarm_timeout,
        default_max_snoozes=max_snoozes,
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "manager": manager,
        "calendar_entity": calendar_entity,
    }

    # Initial sync
    await manager.async_update()

    # Set up periodic updates
    async def async_update_alarms(_now):
        """Update alarms periodically."""
        await manager.async_update()

    entry.async_on_unload(
        async_track_time_interval(
            hass, async_update_alarms, timedelta(seconds=UPDATE_INTERVAL)
        )
    )

    # Set up services
    await async_setup_services(hass)

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Unload services if no more entries
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok

