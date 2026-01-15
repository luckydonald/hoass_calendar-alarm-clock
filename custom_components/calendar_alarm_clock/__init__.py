"""Calendar Alarm Clock integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED, Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.start import async_at_started

from .alarm_manager import AlarmManager
from .const import (
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_ALARM_TIMEOUT,
    CONF_DEFAULT_MAX_SNOOZES,
    CONF_DEFAULT_SNOOZE_DURATION,
    DEFAULT_ALARM_TIMEOUT,
    DEFAULT_MAX_SNOOZES,
    DEFAULT_SNOOZE_DURATION,
    DOMAIN,
    UPDATE_INTERVAL,
)
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
LOVELACE_CARD_URL = "/local/community/calendar_alarm_clock/alarm-clock-card.js"
LOVELACE_CARD_URL_ALT = "/hacsfiles/calendar_alarm_clock/alarm-clock-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Calendar Alarm Clock component."""
    hass.data.setdefault(DOMAIN, {})

    # Register the www folder as static path
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                f"/local/community/{DOMAIN}",
                str(Path(__file__).parent / "www"),
                cache_headers=False,
            )
        ]
    )

    # Set up discovery when HA is fully started
    async def async_discover_on_start(_: HomeAssistant) -> None:
        """Discover calendars when HA starts."""
        await _async_discover_calendars(hass)

    async_at_started(hass, async_discover_on_start)

    # Also listen for new calendar entities being added
    @callback
    def async_state_changed(event: Event) -> None:
        """Handle state changed events to discover new calendars."""
        entity_id: str | None = event.data.get("entity_id")
        if entity_id and entity_id.startswith("calendar."):
            old_state = event.data.get("old_state")
            new_state = event.data.get("new_state")
            # Only trigger discovery if this is a new entity (old_state was None)
            if old_state is None and new_state is not None:
                hass.async_create_task(_async_discover_calendars(hass))

    hass.bus.async_listen(EVENT_STATE_CHANGED, async_state_changed)

    return True


async def _async_discover_calendars(hass: HomeAssistant) -> None:
    """Discover calendars and offer to set up alarm clock."""
    from .config_flow import async_discover_calendars

    await async_discover_calendars(hass)


async def _async_register_card(hass: HomeAssistant) -> None:
    """Register the Lovelace card resource."""
    # Try to register via lovelace resources
    try:
        if "lovelace" in hass.data:
            lovelace_data = hass.data["lovelace"]
            if hasattr(lovelace_data, "resources"):
                resources: ResourceStorageCollection = lovelace_data.resources
                # Check if already registered
                existing = [
                    r
                    for r in resources.async_items()
                    if DOMAIN in r.get("url", "")
                ]
                if not existing:
                    await resources.async_create_item(
                        {
                            "url": LOVELACE_CARD_URL,
                            "res_type": "module",
                        }
                    )
                    _LOGGER.info("Registered Lovelace card resource: %s", LOVELACE_CARD_URL)
    except Exception as e:
        _LOGGER.debug("Could not auto-register Lovelace resource: %s", e)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Calendar Alarm Clock from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    calendar_entity: str = entry.data[CONF_CALENDAR_ENTITY]

    # Get configuration options with defaults
    snooze_duration: int = entry.options.get(
        CONF_DEFAULT_SNOOZE_DURATION, DEFAULT_SNOOZE_DURATION
    )
    alarm_timeout: float = entry.options.get(
        CONF_DEFAULT_ALARM_TIMEOUT, DEFAULT_ALARM_TIMEOUT
    )
    max_snoozes: int = entry.options.get(CONF_DEFAULT_MAX_SNOOZES, DEFAULT_MAX_SNOOZES)

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
    async def async_update_alarms(_now) -> None:
        """Update alarms periodically."""
        await manager.async_update()

    entry.async_on_unload(
        async_track_time_interval(
            hass, async_update_alarms, timedelta(seconds=UPDATE_INTERVAL)
        )
    )

    # Set up services
    await async_setup_services(hass)

    # Register Lovelace card
    await _async_register_card(hass)

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Unload services if no more entries
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok

