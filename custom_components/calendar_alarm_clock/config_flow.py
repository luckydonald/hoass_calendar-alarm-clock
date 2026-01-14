    NumberSelectorMode,
)

from .const import (
    DOMAIN,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_SNOOZE_DURATION,
    CONF_DEFAULT_ALARM_TIMEOUT,
    CONF_DEFAULT_MAX_SNOOZES,
    DEFAULT_SNOOZE_DURATION,
    DEFAULT_ALARM_TIMEOUT,
    DEFAULT_MAX_SNOOZES,
)

_LOGGER = logging.getLogger(__name__)


def get_calendar_entities(hass: HomeAssistant) -> list[str]:
    """Get list of calendar entities."""
    registry = er.async_get(hass)
    return [
        entity.entity_id
        for entity in registry.entities.values()
        if entity.entity_id.startswith("calendar.")
    ]


class CalendarAlarmClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Calendar Alarm Clock."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            calendar_entity = user_input[CONF_CALENDAR_ENTITY]

            # Check if this calendar is already configured
            await self.async_set_unique_id(calendar_entity)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Alarm Clock ({calendar_entity})",
                data={CONF_CALENDAR_ENTITY: calendar_entity},
            )

        # Get available calendar entities
        calendar_entities = get_calendar_entities(self.hass)

        if not calendar_entities:
            return self.async_abort(reason="no_calendars")

        data_schema = vol.Schema(
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Calendar Alarm Clock."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DEFAULT_SNOOZE_DURATION,
                    default=options.get(
                        CONF_DEFAULT_SNOOZE_DURATION, DEFAULT_SNOOZE_DURATION
                    ),
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
                    default=options.get(
                        CONF_DEFAULT_ALARM_TIMEOUT, DEFAULT_ALARM_TIMEOUT
                    ),
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
                    default=options.get(
                        CONF_DEFAULT_MAX_SNOOZES, DEFAULT_MAX_SNOOZES
                    ),
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
"""Config flow for Calendar Alarm Clock integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,

