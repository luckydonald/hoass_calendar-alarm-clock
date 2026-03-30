"""Unit tests for Overview device sensor entities.

Tests OverviewNameSensor (previous / current / next) and TodayCountSensor
(total / upcoming / past) from alarm/core.

All tests are pure unit tests — no HA stack required.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from homeassistant.util import dt as dt_util

from custom_components.calendar_alarm_clock.alarm.core import (
    OverviewNameSensor,
    TodayCountSensor,
)
from custom_components.calendar_alarm_clock.const import DOMAIN
from custom_components.calendar_alarm_clock.models import Alarm

CALENDAR_ENTITY = "calendar.test_cal"
CALENDAR_SUFFIX = "test_cal"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_entry() -> MagicMock:
    entry = MagicMock()
    entry.entry_id = "test-entry-id"
    entry.data = {"calendar_entity": CALENDAR_ENTITY}
    return entry


@pytest.fixture
def mock_manager() -> MagicMock:
    mgr = MagicMock()
    mgr.alarms = {}
    mgr.next_alarm = None
    mgr.previous_alarm = None
    return mgr


def _alarm(
    name: str,
    offset_minutes: float = 60,
    state: str = "before",
    uid: str = "uid-1",
) -> MagicMock:
    now = dt_util.now()
    a = MagicMock(spec=Alarm)
    a.name = name
    a.time = now + timedelta(minutes=offset_minutes)
    a.state = state
    a.id = uid
    return a


# ---------------------------------------------------------------------------
# OverviewNameSensor — unique_id and device_info
# ---------------------------------------------------------------------------


class TestOverviewNameSensorIdentity:
    def test_unique_id_next(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.next.name"

    def test_unique_id_previous(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "previous")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.previous.name"

    def test_unique_id_current(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "current")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.current.name"

    def test_device_info_has_overview_identifier(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        expected_id = (DOMAIN, f"{DOMAIN}.{CALENDAR_SUFFIX}.overview")
        assert expected_id in sensor._attr_device_info["identifiers"]

    def test_all_roles_share_same_device(self, mock_manager, mock_entry) -> None:
        sensors = [OverviewNameSensor(mock_manager, mock_entry, r) for r in ("previous", "current", "next")]
        identifiers = [s._attr_device_info["identifiers"] for s in sensors]
        assert identifiers[0] == identifiers[1] == identifiers[2]


# ---------------------------------------------------------------------------
# OverviewNameSensor — native_value
# ---------------------------------------------------------------------------


class TestOverviewNameSensorValue:
    def test_next_returns_next_alarm_name(self, mock_manager, mock_entry) -> None:
        mock_manager.next_alarm = _alarm("Morning")
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert sensor.native_value == "Morning"

    def test_next_returns_none_when_no_next(self, mock_manager, mock_entry) -> None:
        mock_manager.next_alarm = None
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert sensor.native_value is None

    def test_previous_returns_previous_alarm_name(self, mock_manager, mock_entry) -> None:
        mock_manager.previous_alarm = _alarm("Yesterday's", offset_minutes=-30)
        sensor = OverviewNameSensor(mock_manager, mock_entry, "previous")
        assert sensor.native_value == "Yesterday's"

    def test_previous_returns_none_when_no_previous(self, mock_manager, mock_entry) -> None:
        mock_manager.previous_alarm = None
        sensor = OverviewNameSensor(mock_manager, mock_entry, "previous")
        assert sensor.native_value is None

    def test_current_returns_ringing_alarm_name(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"x": _alarm("Ring!", offset_minutes=-1, state="ringing")}
        sensor = OverviewNameSensor(mock_manager, mock_entry, "current")
        assert sensor.native_value == "Ring!"

    def test_current_returns_ringing_snooze_alarm_name(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"x": _alarm("Re-Ring!", state="ringing_snooze")}
        sensor = OverviewNameSensor(mock_manager, mock_entry, "current")
        assert sensor.native_value == "Re-Ring!"

    def test_current_returns_none_when_nothing_ringing(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"x": _alarm("Future", state="before")}
        sensor = OverviewNameSensor(mock_manager, mock_entry, "current")
        assert sensor.native_value is None

    def test_current_ignores_dismissed_alarm(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"x": _alarm("Done", state="dismissed")}
        sensor = OverviewNameSensor(mock_manager, mock_entry, "current")
        assert sensor.native_value is None


# ---------------------------------------------------------------------------
# OverviewNameSensor — options (ENUM)
# ---------------------------------------------------------------------------


class TestOverviewNameSensorOptions:
    def test_options_empty_when_no_alarms(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert sensor.options == []

    def test_options_includes_all_alarm_names(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {
            "a": _alarm("Alpha", uid="a"),
            "b": _alarm("Beta", uid="b"),
        }
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert set(sensor.options) == {"Alpha", "Beta"}

    def test_options_updates_dynamically(self, mock_manager, mock_entry) -> None:
        sensor = OverviewNameSensor(mock_manager, mock_entry, "next")
        assert sensor.options == []
        mock_manager.alarms = {"c": _alarm("Gamma", uid="c")}
        assert sensor.options == ["Gamma"]


# ---------------------------------------------------------------------------
# TodayCountSensor — unique_id and device_info
# ---------------------------------------------------------------------------


class TestTodayCountSensorIdentity:
    def test_unique_id_total(self, mock_manager, mock_entry) -> None:
        sensor = TodayCountSensor(mock_manager, mock_entry, "total")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.today.total"

    def test_unique_id_upcoming(self, mock_manager, mock_entry) -> None:
        sensor = TodayCountSensor(mock_manager, mock_entry, "upcoming")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.today.upcoming"

    def test_unique_id_past(self, mock_manager, mock_entry) -> None:
        sensor = TodayCountSensor(mock_manager, mock_entry, "past")
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.overview.today.past"

    def test_device_info_has_overview_identifier(self, mock_manager, mock_entry) -> None:
        sensor = TodayCountSensor(mock_manager, mock_entry, "total")
        expected_id = (DOMAIN, f"{DOMAIN}.{CALENDAR_SUFFIX}.overview")
        assert expected_id in sensor._attr_device_info["identifiers"]

    def test_all_roles_share_same_device(self, mock_manager, mock_entry) -> None:
        sensors = [TodayCountSensor(mock_manager, mock_entry, r) for r in ("total", "upcoming", "past")]
        ids = [s._attr_device_info["identifiers"] for s in sensors]
        assert ids[0] == ids[1] == ids[2]


# ---------------------------------------------------------------------------
# TodayCountSensor — native_value
# ---------------------------------------------------------------------------


class TestTodayCountSensorValue:
    def test_total_zero_when_no_alarms(self, mock_manager, mock_entry) -> None:
        sensor = TodayCountSensor(mock_manager, mock_entry, "total")
        assert sensor.native_value == 0

    def test_total_counts_past_and_future_today(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {
            "a": _alarm("Past", offset_minutes=-30, uid="a"),
            "b": _alarm("Future", offset_minutes=30, uid="b"),
        }
        sensor = TodayCountSensor(mock_manager, mock_entry, "total")
        assert sensor.native_value == 2

    def test_total_excludes_other_day_alarms(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {
            "a": _alarm("Today", offset_minutes=30, uid="a"),
            "b": _alarm("Tomorrow", offset_minutes=60 * 25, uid="b"),
        }
        sensor = TodayCountSensor(mock_manager, mock_entry, "total")
        assert sensor.native_value == 1

    def test_upcoming_only_counts_future_today(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {
            "a": _alarm("Past", offset_minutes=-60, uid="a"),
            "b": _alarm("Soon", offset_minutes=30, uid="b"),
            "c": _alarm("Later", offset_minutes=90, uid="c"),
        }
        sensor = TodayCountSensor(mock_manager, mock_entry, "upcoming")
        assert sensor.native_value == 2

    def test_upcoming_zero_when_all_past(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"a": _alarm("Past", offset_minutes=-30, uid="a")}
        sensor = TodayCountSensor(mock_manager, mock_entry, "upcoming")
        assert sensor.native_value == 0

    def test_past_only_counts_past_today(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {
            "a": _alarm("Past", offset_minutes=-30, uid="a"),
            "b": _alarm("Future", offset_minutes=30, uid="b"),
        }
        sensor = TodayCountSensor(mock_manager, mock_entry, "past")
        assert sensor.native_value == 1

    def test_past_zero_when_all_future(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"a": _alarm("Future", offset_minutes=60, uid="a")}
        sensor = TodayCountSensor(mock_manager, mock_entry, "past")
        assert sensor.native_value == 0

    def test_zero_when_no_alarms_today_at_all(self, mock_manager, mock_entry) -> None:
        mock_manager.alarms = {"a": _alarm("Tomorrow", offset_minutes=60 * 25, uid="a")}
        for role in ("total", "upcoming", "past"):
            sensor = TodayCountSensor(mock_manager, mock_entry, role)
            assert sensor.native_value == 0, f"Expected 0 for role={role}"
