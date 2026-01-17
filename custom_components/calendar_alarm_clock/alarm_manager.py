"""Alarm Manager for Calendar Alarm Clock."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .const import (
    EVENT_ALARM_CREATED,
    EVENT_ALARM_DELETED,
    EVENT_ALARM_DISABLED,
    EVENT_ALARM_DISMISSED,
    EVENT_ALARM_EDITED,
    EVENT_ALARM_ENABLED,
    EVENT_ALARM_RINGING,
    EVENT_ALARM_SNOOZED,
    EVENT_ALARM_TIMED_OUT,
    PREFIX_DISABLED,
    PREFIX_DISMISSED,
    PREFIX_SNOOZE,
    STATE_BEFORE,
    STATE_DISMISSED,
    STATE_RINGING,
    STATE_RINGING_SNOOZE,
    STATE_SNOOZED,
    STATE_TIMED_OUT,
    SUFFIX_SNOOZE,
    LOG_NAME,
)
from .models import Alarm

_LOGGER = logging.getLogger(LOG_NAME)


class AlarmManager:
    """Manage alarms and their states."""

    def __init__(
        self,
        hass: HomeAssistant,
        calendar_entity: str,
        default_snooze_duration: int = 9,
        default_alarm_timeout: float = 30.0,
        default_max_snoozes: int = 3,
    ) -> None:
        """Initialize the alarm manager."""
        self.hass: HomeAssistant = hass
        self.calendar_entity: str = calendar_entity
        self.default_snooze_duration: int = default_snooze_duration
        self.default_alarm_timeout: float = default_alarm_timeout
        self.default_max_snoozes: int = default_max_snoozes

        self._alarms: dict[str, Alarm] = {}
        self._listeners: list[Callable[[], None]] = []
        self._timeout_unsubs: dict[str, CALLBACK_TYPE] = {}
        self._next_alarm: Alarm | None = None
        self._previous_alarm: Alarm | None = None

    @property
    def alarms(self) -> dict[str, Alarm]:
        """Get all alarms."""
        return self._alarms

    @property
    def next_alarm(self) -> Alarm | None:
        """Get the next upcoming alarm."""
        return self._next_alarm

    @property
    def previous_alarm(self) -> Alarm | None:
        """Get the previous alarm."""
        return self._previous_alarm

    def add_listener(self, callback_fn: Callable[[], None]) -> Callable[[], None]:
        """Add a listener for alarm updates."""
        self._listeners.append(callback_fn)

        def remove_listener() -> None:
            self._listeners.remove(callback_fn)

        return remove_listener

    def _notify_listeners(self) -> None:
        """Notify all listeners of updates."""
        for callback_fn in self._listeners:
            callback_fn()

    async def async_update(self) -> None:
        """Update alarms from the calendar."""
        now: datetime = dt_util.now()
        start: datetime = now - timedelta(hours=1)  # Include recent past alarms
        end: datetime = now + timedelta(days=7)  # Look ahead one week

        try:
            # Call calendar.get_events service (renamed from list_events in HA 2023.6+)
            result: dict[str, Any] | None = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": self.calendar_entity,
                    "start_date_time": start.isoformat(),
                    "end_date_time": end.isoformat(),
                },
                blocking=True,
                return_response=True,
            )

            if result is None:
                result = {}

            events: list[dict[str, Any]] = result.get(self.calendar_entity, {}).get("events", [])

            # Convert events to alarms
            new_alarms: dict[str, Alarm] = {}
            for event in events:
                alarm: Alarm = Alarm.from_calendar_event(event)

                # Apply defaults
                if alarm.timeout is None:
                    alarm.timeout = self.default_alarm_timeout
                if alarm.max_snoozes is None:
                    alarm.max_snoozes = self.default_max_snoozes
                if alarm.snooze_duration is None:
                    alarm.snooze_duration = self.default_snooze_duration

                # Preserve existing state if alarm already exists
                if alarm.id in self._alarms:
                    existing: Alarm = self._alarms[alarm.id]
                    if existing.state in (STATE_RINGING, STATE_RINGING_SNOOZE, STATE_SNOOZED):
                        alarm.state = existing.state

                new_alarms[alarm.id] = alarm

            self._alarms = new_alarms

            # Update alarm states based on time
            await self._update_alarm_states()

            # Update next/previous alarm references
            self._update_next_previous()

            self._notify_listeners()

        except Exception as e:
            _LOGGER.error("Error updating alarms from calendar: %s", e)

    async def _update_alarm_states(self) -> None:
        """Update alarm states based on current time."""
        now: datetime = dt_util.now()

        for alarm in self._alarms.values():
            if alarm.state == STATE_DISMISSED:
                continue

            if alarm.state == STATE_TIMED_OUT:
                continue

            # Check if alarm should start ringing
            if alarm.state == STATE_BEFORE and alarm.enabled:
                if alarm.time <= now:
                    await self._trigger_alarm(alarm)

            elif (
                alarm.state == STATE_SNOOZED
                and alarm.next_snooze_time
                and alarm.next_snooze_time <= now
            ):
                alarm.state = STATE_RINGING_SNOOZE
                self._fire_event(EVENT_ALARM_RINGING, alarm)
                self._schedule_timeout(alarm)

    async def _trigger_alarm(self, alarm: Alarm) -> None:
        """Trigger an alarm to start ringing."""
        if alarm.snooze_count > 0:
            alarm.state = STATE_RINGING_SNOOZE
        else:
            alarm.state = STATE_RINGING

        self._fire_event(EVENT_ALARM_RINGING, alarm)
        self._schedule_timeout(alarm)

        # Create notification
        await self._create_notification(alarm)

    def _schedule_timeout(self, alarm: Alarm) -> None:
        """Schedule alarm timeout."""
        # Cancel existing timeout
        if alarm.id in self._timeout_unsubs:
            self._timeout_unsubs[alarm.id]()

        timeout_minutes: float = alarm.timeout or self.default_alarm_timeout
        timeout_time: datetime = dt_util.now() + timedelta(minutes=timeout_minutes)

        @callback
        def timeout_callback(_now: datetime) -> None:
            """Handle alarm timeout."""
            if alarm.id in self._alarms:
                alarm.state = STATE_TIMED_OUT
                self._fire_event(EVENT_ALARM_TIMED_OUT, alarm)
                self._notify_listeners()

        self._timeout_unsubs[alarm.id] = async_track_point_in_time(
            self.hass, timeout_callback, timeout_time
        )

    async def _create_notification(self, alarm: Alarm) -> None:
        """Create a notification for a ringing alarm."""
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": f"⏰ {alarm.name}",
                    "message": (
                        f"Alarm '{alarm.name}' is ringing!\n\n"
                        f"Time: {alarm.time.strftime('%H:%M')}\n\n"
                        "Use services to snooze or dismiss."
                    ),
                    "notification_id": f"alarm_clock_{alarm.id}",
                },
            )
        except Exception as e:
            _LOGGER.error("Error creating notification: %s", e)

    async def _dismiss_notification(self, alarm: Alarm) -> None:
        """Dismiss the notification for an alarm."""
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "dismiss",
                {"notification_id": f"alarm_clock_{alarm.id}"},
            )
        except Exception as e:
            _LOGGER.debug("Error dismissing notification: %s", e)

    def _update_next_previous(self) -> None:
        """Update next and previous alarm references."""
        now: datetime = dt_util.now()

        future_alarms: list[Alarm] = [
            a
            for a in self._alarms.values()
            if a.time > now and a.enabled and a.state not in (STATE_DISMISSED, STATE_TIMED_OUT)
        ]
        past_alarms: list[Alarm] = [a for a in self._alarms.values() if a.time <= now]

        future_alarms.sort(key=lambda a: a.time)
        past_alarms.sort(key=lambda a: a.time, reverse=True)

        self._next_alarm = future_alarms[0] if future_alarms else None
        self._previous_alarm = past_alarms[0] if past_alarms else None

    def _fire_event(self, event_type: str, alarm: Alarm) -> None:
        """Fire an event for an alarm."""
        self.hass.bus.async_fire(event_type, alarm.to_dict())

    # --- Service Methods ---

    async def async_create_alarm(
        self,
        name: str = "Alarm",
        time: str | None = None,
        date: str | None = None,
        repeat: str = "none",
        enabled: bool = True,
    ) -> Alarm | None:
        """Create a new alarm."""
        now: datetime = dt_util.now()

        # Parse time
        hour: int
        minute: int
        if time:
            hour, minute = map(int, time.split(":"))
        else:
            hour, minute = now.hour, now.minute

        # Parse date
        alarm_date: datetime
        if date:
            alarm_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            alarm_date = datetime.combine(now.date(), datetime.min.time())

        alarm_datetime: datetime = alarm_date.replace(hour=hour, minute=minute)
        alarm_datetime = dt_util.as_local(alarm_datetime.replace(tzinfo=now.tzinfo))

        # Build event summary
        summary: str = name
        if not enabled:
            summary = f"{PREFIX_DISABLED}{name}"

        # Build recurrence rule
        rrule: str | None = None
        if repeat == "daily":
            rrule = "FREQ=DAILY"
        elif repeat == "weekdays":
            rrule = "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
        elif repeat == "weekends":
            rrule = "FREQ=WEEKLY;BYDAY=SA,SU"
        elif repeat == "weekly":
            rrule = "FREQ=WEEKLY"
        elif repeat != "none":
            rrule = repeat  # Custom RRULE

        # Create calendar event
        service_data: dict[str, Any] = {
            "entity_id": self.calendar_entity,
            "summary": summary,
            "start_date_time": alarm_datetime.isoformat(),
            "end_date_time": (alarm_datetime + timedelta(minutes=1)).isoformat(),
        }

        if rrule:
            service_data["rrule"] = rrule

        try:
            await self.hass.services.async_call(
                "calendar",
                "create_event",
                service_data,
                blocking=True,
            )

            # Refresh alarms
            await self.async_update()

            # Find the newly created alarm
            for alarm in self._alarms.values():
                if alarm.name == name and abs((alarm.time - alarm_datetime).total_seconds()) < 60:
                    self._fire_event(EVENT_ALARM_CREATED, alarm)
                    return alarm

        except Exception as e:
            _LOGGER.error("Error creating alarm: %s", e)

        return None

    async def async_delete_alarm(self, alarm_id: str) -> bool:
        """Delete an alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            _LOGGER.warning("Alarm not found: %s", alarm_id)
            return False

        try:
            await self.hass.services.async_call(
                "calendar",
                "delete_event",
                {
                    "entity_id": self.calendar_entity,
                    "uid": alarm.calendar_event_uid or alarm.base_id,
                },
                blocking=True,
            )

            self._fire_event(EVENT_ALARM_DELETED, alarm)
            del self._alarms[alarm_id]
            self._notify_listeners()
            return True

        except Exception as e:
            _LOGGER.error("Error deleting alarm: %s", e)
            return False

    async def async_snooze_alarm(self, alarm_id: str, duration: int | None = None) -> bool:
        """Snooze an alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            _LOGGER.warning("Alarm not found: %s", alarm_id)
            return False

        if alarm.state not in (STATE_RINGING, STATE_RINGING_SNOOZE):
            _LOGGER.warning("Alarm is not ringing: %s", alarm_id)
            return False

        # Check max snoozes
        if alarm.max_snoozes and alarm.max_snoozes > 0 and alarm.snooze_count >= alarm.max_snoozes:
            _LOGGER.warning("Max snoozes reached for alarm: %s", alarm_id)
            return False

        snooze_duration: int = duration or alarm.snooze_duration or self.default_snooze_duration
        snooze_time: datetime = dt_util.now() + timedelta(minutes=snooze_duration)
        new_snooze_count: int = alarm.snooze_count + 1

        # Create snoozed event in calendar
        snooze_summary: str = f"{PREFIX_SNOOZE.format(new_snooze_count)}{alarm.name}"
        snooze_id: str = f"{alarm.base_id}{SUFFIX_SNOOZE.format(new_snooze_count)}"

        try:
            await self.hass.services.async_call(
                "calendar",
                "create_event",
                {
                    "entity_id": self.calendar_entity,
                    "summary": snooze_summary,
                    "start_date_time": snooze_time.isoformat(),
                    "end_date_time": (snooze_time + timedelta(minutes=1)).isoformat(),
                    "uid": snooze_id,
                },
                blocking=True,
            )

            # Update current alarm state
            alarm.state = STATE_SNOOZED
            alarm.next_snooze_time = snooze_time

            # Cancel timeout
            if alarm_id in self._timeout_unsubs:
                self._timeout_unsubs[alarm_id]()
                del self._timeout_unsubs[alarm_id]

            await self._dismiss_notification(alarm)
            self._fire_event(EVENT_ALARM_SNOOZED, alarm)
            self._notify_listeners()

            # Refresh alarms
            await self.async_update()

            return True

        except Exception as e:
            _LOGGER.error("Error snoozing alarm: %s", e)
            return False

    async def async_dismiss_alarm(self, alarm_id: str) -> bool:
        """Dismiss an alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            _LOGGER.warning("Alarm not found: %s", alarm_id)
            return False

        # Update calendar event with dismissed prefix
        dismissed_summary: str = f"{PREFIX_DISMISSED}{alarm.name}"

        try:
            # Note: Updating calendar events may vary by integration
            # This is a simplified approach
            await self.hass.services.async_call(
                "calendar",
                "update_event",
                {
                    "entity_id": self.calendar_entity,
                    "uid": alarm.calendar_event_uid or alarm.id,
                    "summary": dismissed_summary,
                },
                blocking=True,
            )
        except Exception as e:
            _LOGGER.debug("Could not update calendar event: %s", e)

        # Update alarm state
        alarm.state = STATE_DISMISSED

        # Cancel timeout
        if alarm_id in self._timeout_unsubs:
            self._timeout_unsubs[alarm_id]()
            del self._timeout_unsubs[alarm_id]

        await self._dismiss_notification(alarm)
        self._fire_event(EVENT_ALARM_DISMISSED, alarm)
        self._notify_listeners()

        return True

    async def async_enable_alarm(self, alarm_id: str) -> bool:
        """Enable an alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            return False

        if alarm.enabled:
            return True

        # Remove DISABLED prefix from calendar event
        try:
            await self.hass.services.async_call(
                "calendar",
                "update_event",
                {
                    "entity_id": self.calendar_entity,
                    "uid": alarm.calendar_event_uid or alarm.id,
                    "summary": alarm.name,  # Without prefix
                },
                blocking=True,
            )
        except Exception as e:
            _LOGGER.debug("Could not update calendar event: %s", e)

        alarm.enabled = True
        self._fire_event(EVENT_ALARM_ENABLED, alarm)
        self._notify_listeners()

        return True

    async def async_disable_alarm(self, alarm_id: str) -> bool:
        """Disable an alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            return False

        if not alarm.enabled:
            return True

        # Add DISABLED prefix to calendar event
        disabled_summary: str = f"{PREFIX_DISABLED}{alarm.name}"

        try:
            await self.hass.services.async_call(
                "calendar",
                "update_event",
                {
                    "entity_id": self.calendar_entity,
                    "uid": alarm.calendar_event_uid or alarm.id,
                    "summary": disabled_summary,
                },
                blocking=True,
            )
        except Exception as e:
            _LOGGER.debug("Could not update calendar event: %s", e)

        alarm.enabled = False
        self._fire_event(EVENT_ALARM_DISABLED, alarm)
        self._notify_listeners()

        return True

    async def async_trigger_alarm(self, alarm_id: str) -> bool:
        """Manually trigger an alarm for testing."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            return False

        await self._trigger_alarm(alarm)
        self._notify_listeners()

        return True

    async def async_edit_alarm(
        self,
        alarm_id: str,
        name: str | None = None,
        time: str | None = None,
        repeat: str | None = None,
        enabled: bool | None = None,
    ) -> bool:
        """Edit an existing alarm."""
        alarm: Alarm | None = self._alarms.get(alarm_id)
        if not alarm:
            return False

        # Build updated summary
        new_name: str = name if name is not None else alarm.name
        new_enabled: bool = enabled if enabled is not None else alarm.enabled

        summary: str = new_name
        if not new_enabled:
            summary = f"{PREFIX_DISABLED}{new_name}"

        # Build service data
        service_data: dict[str, Any] = {
            "entity_id": self.calendar_entity,
            "uid": alarm.calendar_event_uid or alarm.id,
            "summary": summary,
        }

        if time:
            hour, minute = map(int, time.split(":"))
            new_time: datetime = alarm.time.replace(hour=hour, minute=minute)
            service_data["start_date_time"] = new_time.isoformat()
            service_data["end_date_time"] = (new_time + timedelta(minutes=1)).isoformat()

        if repeat is not None:
            if repeat == "daily":
                service_data["rrule"] = "FREQ=DAILY"
            elif repeat == "weekdays":
                service_data["rrule"] = "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
            elif repeat == "weekends":
                service_data["rrule"] = "FREQ=WEEKLY;BYDAY=SA,SU"
            elif repeat == "weekly":
                service_data["rrule"] = "FREQ=WEEKLY"
            elif repeat != "none":
                service_data["rrule"] = repeat

        try:
            await self.hass.services.async_call(
                "calendar",
                "update_event",
                service_data,
                blocking=True,
            )

            self._fire_event(EVENT_ALARM_EDITED, alarm)
            await self.async_update()

            return True

        except Exception as e:
            _LOGGER.error("Error editing alarm: %s", e)
            return False

    def list_alarms(self) -> list[dict[str, Any]]:
        """List all alarms."""
        return [alarm.to_dict() for alarm in self._alarms.values()]
