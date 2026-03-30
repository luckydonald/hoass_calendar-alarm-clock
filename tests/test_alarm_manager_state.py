"""Unit tests for AlarmManager state machine logic.

Uses a lightweight mock HomeAssistant so the full HA stack is not needed.
Calendar service calls are mocked at hass.services level.

Covers:
- Loading alarms from calendar events
- State transitions (before → ringing on time, dismissed/disabled skip ringing)
- HA event firing (alarm_ringing, alarm_snoozed, alarm_dismissed, etc.)
- next_alarm / previous_alarm tracking
- Snooze: success path, not-ringing guard, max-snoozes limit
- Dismiss: success path, unknown-id guard
- Enable / disable toggle
- Listener notification
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.util import dt as dt_util

from custom_components.calendar_alarm_clock.alarm_manager import AlarmManager
from custom_components.calendar_alarm_clock.const import (
    EVENT_ALARM_DISMISSED,
    EVENT_ALARM_DISABLED,
    EVENT_ALARM_ENABLED,
    EVENT_ALARM_RINGING,
    EVENT_ALARM_SNOOZED,
)

CALENDAR_ENTITY = "calendar.test_alarms"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_event(
    summary: str,
    offset_minutes: float = 60,
    uid: str = "alarm-1",
    rrule: str | None = None,
) -> dict:
    """Return a calendar event dict with start time relative to now."""
    start = dt_util.now() + timedelta(minutes=offset_minutes)
    return {"summary": summary, "start": start.isoformat(), "uid": uid, "rrule": rrule}


def _calendar_response(*events: dict) -> dict:
    """Wrap events in the format returned by the calendar.get_events service."""
    return {CALENDAR_ENTITY: {"events": list(events)}}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_hass():
    """Minimal mock HomeAssistant with services wired up."""
    hass = MagicMock()
    hass.services.has_service = MagicMock(return_value=True)
    hass.services.async_call = AsyncMock(return_value=_calendar_response())
    hass.bus.async_fire = MagicMock()
    return hass


@pytest.fixture
def manager(mock_hass):
    return AlarmManager(
        hass=mock_hass,
        calendar_entity=CALENDAR_ENTITY,
        default_snooze_duration=9,
        default_alarm_timeout=30.0,
        default_max_snoozes=3,
    )


# Patch the HA timer helper so tests don't schedule real callbacks
_patch_timer = patch(
    "custom_components.calendar_alarm_clock.alarm_manager.async_track_point_in_time",
    return_value=MagicMock(),
)


# ---------------------------------------------------------------------------
# Loading alarms
# ---------------------------------------------------------------------------


class TestAlarmLoading:
    async def test_alarms_populated_after_update(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Morning Alarm", offset_minutes=30)
        )
        with _patch_timer:
            await manager.async_update()
        assert len(manager.alarms) == 1

    async def test_alarm_name_parsed(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("My Alarm", offset_minutes=30)
        )
        with _patch_timer:
            await manager.async_update()
        alarm = next(iter(manager.alarms.values()))
        assert alarm.name == "My Alarm"

    async def test_multiple_alarms_loaded(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Alarm A", offset_minutes=30, uid="a"),
            _make_event("Alarm B", offset_minutes=60, uid="b"),
        )
        with _patch_timer:
            await manager.async_update()
        assert len(manager.alarms) == 2

    async def test_empty_calendar_gives_no_alarms(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response()
        with _patch_timer:
            await manager.async_update()
        assert len(manager.alarms) == 0

    async def test_listeners_notified_after_update(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response()
        listener = MagicMock()
        manager.add_listener(listener)
        with _patch_timer:
            await manager.async_update()
        listener.assert_called_once()


# ---------------------------------------------------------------------------
# State transitions
# ---------------------------------------------------------------------------


class TestStateTransitions:
    async def test_future_alarm_stays_before(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Future", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm = next(iter(manager.alarms.values()))
        assert alarm.state == "before"

    async def test_past_alarm_transitions_to_ringing(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Past", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm = next(iter(manager.alarms.values()))
        assert alarm.state == "ringing"

    async def test_dismissed_alarm_does_not_ring(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISMISSED] Old", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm = next(iter(manager.alarms.values()))
        assert alarm.state == "dismissed"

    async def test_disabled_alarm_does_not_ring(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISABLED] Muted", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm = next(iter(manager.alarms.values()))
        assert alarm.state == "before"  # time passed but disabled — stays before


# ---------------------------------------------------------------------------
# Event firing
# ---------------------------------------------------------------------------


class TestEventFiring:
    def _fired_event_types(self, mock_hass) -> list[str]:
        return [c.args[0] for c in mock_hass.bus.async_fire.call_args_list]

    async def test_alarm_ringing_event_fired(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Ring", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        assert EVENT_ALARM_RINGING in self._fired_event_types(mock_hass)

    async def test_no_ringing_event_for_future_alarm(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Future", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        assert EVENT_ALARM_RINGING not in self._fired_event_types(mock_hass)

    async def test_no_ringing_event_for_dismissed_alarm(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISMISSED] Done", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        assert EVENT_ALARM_RINGING not in self._fired_event_types(mock_hass)


# ---------------------------------------------------------------------------
# next_alarm / previous_alarm
# ---------------------------------------------------------------------------


class TestNextPreviousAlarm:
    async def test_next_alarm_is_soonest_future(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Far", offset_minutes=120, uid="far"),
            _make_event("Soon", offset_minutes=30, uid="soon"),
        )
        with _patch_timer:
            await manager.async_update()
        assert manager.next_alarm is not None
        assert manager.next_alarm.name == "Soon"

    async def test_previous_alarm_is_most_recent_past(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Old", offset_minutes=-120, uid="old"),
            _make_event("Recent", offset_minutes=-10, uid="recent"),
        )
        with _patch_timer:
            await manager.async_update()
        assert manager.previous_alarm is not None
        assert manager.previous_alarm.name == "Recent"

    async def test_next_alarm_is_none_when_no_future_alarms(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Past", offset_minutes=-30)
        )
        with _patch_timer:
            await manager.async_update()
        assert manager.next_alarm is None

    async def test_previous_alarm_is_none_when_no_past_alarms(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Future", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        assert manager.previous_alarm is None

    async def test_dismissed_alarm_excluded_from_next(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISMISSED] Done", offset_minutes=30, uid="dismissed"),
            _make_event("Active", offset_minutes=60, uid="active"),
        )
        with _patch_timer:
            await manager.async_update()
        assert manager.next_alarm is not None
        assert manager.next_alarm.name == "Active"


# ---------------------------------------------------------------------------
# Snooze
# ---------------------------------------------------------------------------


class TestSnooze:
    async def _setup_ringing(self, manager, mock_hass, uid: str = "alarm-1") -> str:
        """Set up a ringing alarm and return its id."""
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Ring", offset_minutes=-1, uid=uid)
        )
        with _patch_timer:
            await manager.async_update()
        return next(id for id in manager.alarms if uid in id)

    async def test_snooze_returns_true_for_ringing_alarm(self, manager, mock_hass) -> None:
        alarm_id = await self._setup_ringing(manager, mock_hass)
        mock_hass.services.async_call.return_value = _calendar_response()
        with _patch_timer:
            result = await manager.async_snooze_alarm(alarm_id)
        assert result is True

    async def test_snooze_sets_state_to_snoozed(self, manager, mock_hass) -> None:
        alarm_id = await self._setup_ringing(manager, mock_hass)
        mock_hass.services.async_call.return_value = _calendar_response()
        with _patch_timer:
            await manager.async_snooze_alarm(alarm_id)
        assert manager.alarms[alarm_id].state == "snoozed"

    async def test_snooze_fires_snoozed_event(self, manager, mock_hass) -> None:
        alarm_id = await self._setup_ringing(manager, mock_hass)
        mock_hass.bus.async_fire.reset_mock()
        mock_hass.services.async_call.return_value = _calendar_response()
        with _patch_timer:
            await manager.async_snooze_alarm(alarm_id)
        fired = [c.args[0] for c in mock_hass.bus.async_fire.call_args_list]
        assert EVENT_ALARM_SNOOZED in fired

    async def test_snooze_non_ringing_alarm_returns_false(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Future", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        result = await manager.async_snooze_alarm(alarm_id)
        assert result is False

    async def test_snooze_unknown_alarm_returns_false(self, manager, mock_hass) -> None:
        result = await manager.async_snooze_alarm("no-such-id")
        assert result is False

    async def test_snooze_at_max_snoozes_returns_false(self, manager, mock_hass) -> None:
        alarm_id = await self._setup_ringing(manager, mock_hass)
        alarm = manager.alarms[alarm_id]
        alarm.snooze_count = 3
        alarm.max_snoozes = 3
        result = await manager.async_snooze_alarm(alarm_id)
        assert result is False

    async def test_snooze_with_infinite_max_snoozes(self, manager, mock_hass) -> None:
        """max_snoozes=0 means infinite; snooze should succeed regardless of count."""
        alarm_id = await self._setup_ringing(manager, mock_hass)
        alarm = manager.alarms[alarm_id]
        alarm.snooze_count = 99
        alarm.max_snoozes = 0  # 0 = no limit
        mock_hass.services.async_call.return_value = _calendar_response()
        with _patch_timer:
            result = await manager.async_snooze_alarm(alarm_id)
        assert result is True


# ---------------------------------------------------------------------------
# Dismiss
# ---------------------------------------------------------------------------


class TestDismiss:
    async def test_dismiss_sets_state_dismissed(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Ring", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        await manager.async_dismiss_alarm(alarm_id)
        assert manager.alarms[alarm_id].state == "dismissed"

    async def test_dismiss_fires_dismissed_event(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Ring", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        mock_hass.bus.async_fire.reset_mock()
        await manager.async_dismiss_alarm(alarm_id)
        fired = [c.args[0] for c in mock_hass.bus.async_fire.call_args_list]
        assert EVENT_ALARM_DISMISSED in fired

    async def test_dismiss_unknown_alarm_returns_false(self, manager, mock_hass) -> None:
        result = await manager.async_dismiss_alarm("no-such-id")
        assert result is False

    async def test_dismiss_returns_true_on_success(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Ring", offset_minutes=-1)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        result = await manager.async_dismiss_alarm(alarm_id)
        assert result is True


# ---------------------------------------------------------------------------
# Enable / Disable
# ---------------------------------------------------------------------------


class TestEnableDisable:
    async def test_enable_sets_enabled_true(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISABLED] Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        assert manager.alarms[alarm_id].enabled is False
        await manager.async_enable_alarm(alarm_id)
        assert manager.alarms[alarm_id].enabled is True

    async def test_enable_fires_enabled_event(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISABLED] Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        mock_hass.bus.async_fire.reset_mock()
        await manager.async_enable_alarm(alarm_id)
        fired = [c.args[0] for c in mock_hass.bus.async_fire.call_args_list]
        assert EVENT_ALARM_ENABLED in fired

    async def test_disable_sets_enabled_false(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        assert manager.alarms[alarm_id].enabled is True
        await manager.async_disable_alarm(alarm_id)
        assert manager.alarms[alarm_id].enabled is False

    async def test_disable_fires_disabled_event(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        mock_hass.bus.async_fire.reset_mock()
        await manager.async_disable_alarm(alarm_id)
        fired = [c.args[0] for c in mock_hass.bus.async_fire.call_args_list]
        assert EVENT_ALARM_DISABLED in fired

    async def test_enable_already_enabled_is_noop(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        result = await manager.async_enable_alarm(alarm_id)
        assert result is True  # returns True as success, no changes needed

    async def test_disable_already_disabled_is_noop(self, manager, mock_hass) -> None:
        mock_hass.services.async_call.return_value = _calendar_response(
            _make_event("[DISABLED] Alarm", offset_minutes=60)
        )
        with _patch_timer:
            await manager.async_update()
        alarm_id = next(iter(manager.alarms))
        result = await manager.async_disable_alarm(alarm_id)
        assert result is True
