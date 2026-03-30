"""Unit tests for AlarmEntryBinarySensor (alarm/entries).

Each calendar event gets its own device and a .ringing binary sensor.
Tests cover: unique_id format, device_info (per-entry identifier + via_device
link to overview), is_on for every alarm state, extra_state_attributes
(all required keys, alarm_state value), availability, and dynamic update helpers.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.util import dt as dt_util

from custom_components.calendar_alarm_clock.alarm.entries import AlarmEntryBinarySensor
from custom_components.calendar_alarm_clock.const import DOMAIN
from custom_components.calendar_alarm_clock.models import Alarm

CALENDAR_ENTITY = "calendar.my_cal"
CALENDAR_SUFFIX = "my_cal"


@contextmanager
def _no_ha_state_write(sensor: AlarmEntryBinarySensor):
    """Suppress async_write_ha_state for entities not registered in HA."""
    with patch.object(sensor, "async_write_ha_state"):
        yield

# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

REQUIRED_ATTRIBUTES = (
    "alarm_id",
    "name",
    "time",
    "enabled",
    "repeat",
    "next_snooze_time",
    "snooze_count",
    "timeout",
    "max_snoozes",
    "alarm_state",
)


@pytest.fixture
def mock_entry() -> MagicMock:
    entry = MagicMock()
    entry.entry_id = "entry-id-1"
    entry.data = {"calendar_entity": CALENDAR_ENTITY}
    return entry


@pytest.fixture
def mock_manager() -> MagicMock:
    return MagicMock()


def _alarm(
    state: str = "before",
    name: str = "Test Alarm",
    uid: str = "event-123",
    snooze_count: int = 0,
    enabled: bool = True,
    repeat: str = "none",
) -> MagicMock:
    now = dt_util.now()
    a = MagicMock(spec=Alarm)
    a.id = uid
    a.name = name
    a.time = now + timedelta(minutes=30)
    a.state = state
    a.enabled = enabled
    a.repeat = repeat
    a.next_snooze_time = None
    a.snooze_count = snooze_count
    a.timeout = 30.0
    a.max_snoozes = 3
    return a


# ---------------------------------------------------------------------------
# unique_id
# ---------------------------------------------------------------------------


class TestUniqueId:
    def test_unique_id_format(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="evt-abc"))
        assert sensor._attr_unique_id == f"{DOMAIN}.{CALENDAR_SUFFIX}.entry.evt-abc.ringing"

    def test_unique_id_includes_calendar_suffix(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="x"))
        assert CALENDAR_SUFFIX in sensor._attr_unique_id

    def test_different_events_have_different_unique_ids(self, mock_manager, mock_entry) -> None:
        s1 = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="uid-1"))
        s2 = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="uid-2"))
        assert s1._attr_unique_id != s2._attr_unique_id


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------


class TestDeviceInfo:
    def test_device_identifier_per_entry(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="evt-1"))
        expected = (DOMAIN, f"{DOMAIN}.{CALENDAR_SUFFIX}.entry.evt-1")
        assert expected in sensor.device_info["identifiers"]

    def test_different_events_have_different_device_identifiers(self, mock_manager, mock_entry) -> None:
        s1 = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="uid-1"))
        s2 = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="uid-2"))
        assert s1.device_info["identifiers"] != s2.device_info["identifiers"]

    def test_via_device_links_to_overview(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="evt-1"))
        expected_via = (DOMAIN, f"{DOMAIN}.{CALENDAR_SUFFIX}.overview")
        assert sensor.device_info.get("via_device") == expected_via

    def test_device_name_includes_alarm_name(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(name="Wake Up", uid="e"))
        assert "Wake Up" in sensor.device_info["name"]


# ---------------------------------------------------------------------------
# is_on: True only when ringing
# ---------------------------------------------------------------------------


class TestIsOn:
    @pytest.mark.parametrize("state", ["ringing", "ringing_snooze"])
    def test_is_on_when_actively_ringing(self, mock_manager, mock_entry, state: str) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(state=state))
        assert sensor.is_on is True

    @pytest.mark.parametrize("state", ["before", "snoozed", "dismissed", "timed_out"])
    def test_is_off_when_not_ringing(self, mock_manager, mock_entry, state: str) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(state=state))
        assert sensor.is_on is False


# ---------------------------------------------------------------------------
# extra_state_attributes
# ---------------------------------------------------------------------------


class TestAttributes:
    def test_all_required_keys_present(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        attrs = sensor.extra_state_attributes
        for key in REQUIRED_ATTRIBUTES:
            assert key in attrs, f"Missing attribute: {key}"

    def test_alarm_state_matches_alarm_state(self, mock_manager, mock_entry) -> None:
        for state in ("before", "ringing", "snoozed", "dismissed", "timed_out"):
            sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(state=state))
            assert sensor.extra_state_attributes["alarm_state"] == state

    def test_name_attribute_matches_alarm_name(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(name="My Alarm"))
        assert sensor.extra_state_attributes["name"] == "My Alarm"

    def test_alarm_id_attribute_matches_uid(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(uid="my-uid"))
        assert sensor.extra_state_attributes["alarm_id"] == "my-uid"

    def test_snooze_count_attribute(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(snooze_count=2))
        assert sensor.extra_state_attributes["snooze_count"] == 2

    def test_enabled_attribute(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(enabled=False))
        assert sensor.extra_state_attributes["enabled"] is False

    def test_repeat_attribute(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(repeat="daily"))
        assert sensor.extra_state_attributes["repeat"] == "daily"

    def test_time_attribute_is_iso_string(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        t = sensor.extra_state_attributes["time"]
        assert isinstance(t, str)
        assert "T" in t

    def test_next_snooze_time_none_by_default(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        assert sensor.extra_state_attributes["next_snooze_time"] is None


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------


class TestAvailability:
    def test_available_true_by_default(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        assert sensor.available is True

    def test_set_unavailable_marks_unavailable(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        with _no_ha_state_write(sensor):
            sensor.async_set_unavailable()
        assert sensor.available is False


# ---------------------------------------------------------------------------
# Dynamic update helpers
# ---------------------------------------------------------------------------


class TestUpdateHelpers:
    def test_update_from_alarm_changes_state(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(state="before"))
        assert sensor.is_on is False
        with _no_ha_state_write(sensor):
            sensor.async_update_from_alarm(_alarm(state="ringing"))
        assert sensor.is_on is True

    def test_update_from_alarm_restores_availability(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        with _no_ha_state_write(sensor):
            sensor.async_set_unavailable()
        assert sensor.available is False
        with _no_ha_state_write(sensor):
            sensor.async_update_from_alarm(_alarm())
        assert sensor.available is True

    def test_update_from_alarm_updates_name(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm(name="Old"))
        with _no_ha_state_write(sensor):
            sensor.async_update_from_alarm(_alarm(name="New"))
        assert sensor.extra_state_attributes["name"] == "New"

    def test_set_unavailable_then_update_recovers(self, mock_manager, mock_entry) -> None:
        sensor = AlarmEntryBinarySensor(mock_manager, mock_entry, _alarm())
        with _no_ha_state_write(sensor):
            sensor.async_set_unavailable()
        with _no_ha_state_write(sensor):
            sensor.async_update_from_alarm(_alarm(state="ringing"))
        assert sensor.available is True
        assert sensor.is_on is True
