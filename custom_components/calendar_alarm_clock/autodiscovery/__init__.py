"""Auto-discovery helpers for Calendar backed Alarm Clock."""

from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..const import CONF_AUTO_DISCOVER_CALENDARS, CONF_CALENDAR_ENTITY, DOMAIN, LOG_NAME

_LOGGER = logging.getLogger(LOG_NAME)


def get_calendar_entities(hass: HomeAssistant) -> list[str]:
    """Get list of calendar entities."""
    calendar_entities: list[str] = list(hass.states.async_entity_ids("calendar"))

    # Also check entity registry for any that might not have state yet
    registry = er.async_get(hass)
    for entity in registry.entities.values():
        if entity.entity_id.startswith("calendar.") and entity.entity_id not in calendar_entities:
            calendar_entities.append(entity.entity_id)

    return sorted(calendar_entities)


def get_unconfigured_calendars(hass: HomeAssistant) -> list[str]:
    """Get calendar entities that are not yet configured for alarm clock."""
    all_calendars = get_calendar_entities(hass)

    configured_calendars: set[str] = set()
    for entry in hass.config_entries.async_entries(DOMAIN):
        if CONF_CALENDAR_ENTITY in entry.data:
            configured_calendars.add(entry.data[CONF_CALENDAR_ENTITY])

    return [cal for cal in all_calendars if cal not in configured_calendars]


async def async_auto_create_discovery_entry(hass: HomeAssistant) -> None:
    """Auto-create the auto-discovery config entry if calendars exist and it's not configured."""
    has_auto_discovery = False
    has_manual_entries = False

    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_AUTO_DISCOVER_CALENDARS, False):
            has_auto_discovery = True
        else:
            has_manual_entries = True

    if has_auto_discovery:
        _LOGGER.debug("Auto-discovery entry already exists")
        return

    if has_manual_entries:
        _LOGGER.debug("User has manually configured calendar entries, skipping auto-discovery")
        return

    calendars = get_calendar_entities(hass)
    if not calendars:
        _LOGGER.debug("No calendars found, skipping auto-discovery entry creation")
        return

    _LOGGER.info("Found %d calendar(s), will create auto-discovery entry", len(calendars))

    existing_flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    _LOGGER.debug("Existing flows: %r", existing_flows)
    if any(flow.get("context", {}).get("unique_id") == "auto_discovery" for flow in existing_flows):
        _LOGGER.debug("Auto-discovery flow already in progress")
        return

    _LOGGER.info("Creating auto-discovery flow...")
    await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
        data={CONF_AUTO_DISCOVER_CALENDARS: True},
    )


async def async_discover_calendars(hass: HomeAssistant) -> None:
    """Discover unconfigured calendars and create discovery flows for each."""
    auto_discovery_enabled = any(
        entry.data.get(CONF_AUTO_DISCOVER_CALENDARS, False)
        for entry in hass.config_entries.async_entries(DOMAIN)
    )

    if not auto_discovery_enabled:
        _LOGGER.debug("Auto-discovery is disabled, skipping calendar discovery")
        return

    unconfigured = get_unconfigured_calendars(hass)

    for calendar_entity in unconfigured:
        existing_flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
        if any(
            flow.get("context", {}).get("unique_id") == calendar_entity
            for flow in existing_flows
        ):
            continue

        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
                data={CONF_CALENDAR_ENTITY: calendar_entity},
            )
        )
