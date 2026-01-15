"""Config flow for Calendar Alarm Clock integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import onboarding
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_ALARM_TIMEOUT,
    CONF_DEFAULT_MAX_SNOOZES,
    CONF_DEFAULT_SNOOZE_DURATION,
    DEFAULT_ALARM_TIMEOUT,
    DEFAULT_MAX_SNOOZES,
    DEFAULT_SNOOZE_DURATION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def get_calendar_entities(hass: HomeAssistant) -> list[str]:
    """Get list of calendar entities."""
    # Get calendars from hass.states (more reliable than entity registry)
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

    # Get already configured calendars
    configured_calendars: set[str] = set()
    for entry in hass.config_entries.async_entries(DOMAIN):
        if CONF_CALENDAR_ENTITY in entry.data:
            configured_calendars.add(entry.data[CONF_CALENDAR_ENTITY])

    return [cal for cal in all_calendars if cal not in configured_calendars]


class CalendarAlarmClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Calendar Alarm Clock."""

    VERSION: int = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_calendar: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step (manual setup)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            calendar_entity: str = user_input[CONF_CALENDAR_ENTITY]

            # Check if this calendar is already configured
            await self.async_set_unique_id(calendar_entity)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Alarm Clock ({calendar_entity.split('.')[-1]})",
                data={CONF_CALENDAR_ENTITY: calendar_entity},
            )

        # Get available calendar entities
        calendar_entities: list[str] = get_calendar_entities(self.hass)
        _LOGGER.debug("Found calendar entities: %s", calendar_entities)

        if not calendar_entities:
            return self.async_abort(reason="no_calendars")

        data_schema: vol.Schema = vol.Schema(
            {
                vol.Required(CONF_CALENDAR_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="calendar")
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_integration_discovery(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle discovery of a calendar entity."""
        calendar_entity: str = discovery_info[CONF_CALENDAR_ENTITY]

        # Check if this calendar is already configured
        await self.async_set_unique_id(calendar_entity)
        self._abort_if_unique_id_configured()

        self._discovered_calendar = calendar_entity

        # Set a nice title for the discovery notification
        calendar_name = calendar_entity.split(".")[-1].replace("_", " ").title()
        self.context["title_placeholders"] = {"name": calendar_name}

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm the discovered calendar setup."""
        if user_input is not None or not onboarding.async_is_onboarded(self.hass):
            # User confirmed or onboarding is not complete (auto-setup)
            assert self._discovered_calendar is not None
            calendar_name = self._discovered_calendar.split(".")[-1].replace("_", " ").title()
            return self.async_create_entry(
                title=f"Alarm Clock ({calendar_name})",
                data={CONF_CALENDAR_ENTITY: self._discovered_calendar},
            )

        calendar_name = (
            self._discovered_calendar.split(".")[-1].replace("_", " ").title()
            if self._discovered_calendar
            else "Unknown"
        )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"calendar": calendar_name},
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Calendar Alarm Clock."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry: config_entries.ConfigEntry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options: dict[str, Any] = dict(self.config_entry.options)

        data_schema: vol.Schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DEFAULT_SNOOZE_DURATION,
                    default=options.get(CONF_DEFAULT_SNOOZE_DURATION, DEFAULT_SNOOZE_DURATION),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=60,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="minutes",
                    )
                ),
                vol.Optional(
                    CONF_DEFAULT_ALARM_TIMEOUT,
                    default=options.get(CONF_DEFAULT_ALARM_TIMEOUT, DEFAULT_ALARM_TIMEOUT),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=120,
                        step=0.5,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="minutes",
                    )
                ),
                vol.Optional(
                    CONF_DEFAULT_MAX_SNOOZES,
                    default=options.get(CONF_DEFAULT_MAX_SNOOZES, DEFAULT_MAX_SNOOZES),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=0,
                        max=20,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )


async def async_discover_calendars(hass: HomeAssistant) -> None:
    """Discover calendars and create discovery flows."""
    unconfigured = get_unconfigured_calendars(hass)

    for calendar_entity in unconfigured:
        # Check if there's already a pending flow for this calendar
        existing_flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
        if any(
            flow.get("context", {}).get("unique_id") == calendar_entity for flow in existing_flows
        ):
            continue

        # Create a discovery flow
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
                data={CONF_CALENDAR_ENTITY: calendar_entity},
            )
        )
