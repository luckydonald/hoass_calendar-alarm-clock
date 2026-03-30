"""Unit tests for Alarm model parsing from calendar events.

Covers Alarm.from_calendar_event for all supported prefixes (SNOOZE, DISMISSED,
DISABLED), RRULE repeat modes, id/base_id derivation, and to_dict serialisation.
"""

from __future__ import annotations

import pytest

from custom_components.calendar_alarm_clock.models import Alarm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_event(
    summary: str,
    start: str = "2026-04-01T08:00:00+00:00",
    uid: str = "test-uid-1",
    rrule: str | None = None,
) -> dict:
    """Return a minimal calendar event dict."""
    return {"summary": summary, "start": start, "uid": uid, "rrule": rrule}


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------


class TestBasicAlarm:
    def test_name_parsed(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Morning Alarm"))
        assert alarm.name == "Morning Alarm"

    def test_uid_becomes_id(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm", uid="my-uid"))
        assert alarm.id == "my-uid"

    def test_default_state_is_before(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm"))
        assert alarm.state == "before"

    def test_default_enabled_true(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm"))
        assert alarm.enabled is True

    def test_default_snooze_count_zero(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm"))
        assert alarm.snooze_count == 0

    def test_time_parsed_from_iso_string(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm", start="2026-04-01T08:30:00+00:00"))
        assert alarm.time.hour == 8
        assert alarm.time.minute == 30

    def test_no_rrule_gives_none_repeat(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm"))
        assert alarm.repeat == "none"


# ---------------------------------------------------------------------------
# Prefix: [SNOOZE n]
# ---------------------------------------------------------------------------


class TestSnoozePrefix:
    def test_snooze_count_extracted(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 1] Morning Alarm", uid="base"))
        assert alarm.snooze_count == 1

    def test_snooze_count_2(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 2] Morning Alarm", uid="base"))
        assert alarm.snooze_count == 2

    def test_name_stripped_of_snooze_prefix(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 1] Morning Alarm"))
        assert alarm.name == "Morning Alarm"

    def test_id_gets_snooze_suffix(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 1] Morning Alarm", uid="base"))
        assert alarm.id == "base-snooze-1"

    def test_id_snooze_3(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 3] Alarm", uid="uid-x"))
        assert alarm.id == "uid-x-snooze-3"


# ---------------------------------------------------------------------------
# Prefix: [DISMISSED]
# ---------------------------------------------------------------------------


class TestDismissedPrefix:
    def test_state_is_dismissed(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISMISSED] Morning Alarm"))
        assert alarm.state == "dismissed"

    def test_name_stripped_of_dismissed_prefix(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISMISSED] Morning Alarm"))
        assert alarm.name == "Morning Alarm"

    def test_enabled_unchanged_by_dismissed(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISMISSED] Morning Alarm"))
        assert alarm.enabled is True


# ---------------------------------------------------------------------------
# Prefix: [DISABLED]
# ---------------------------------------------------------------------------


class TestDisabledPrefix:
    def test_enabled_is_false(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISABLED] Morning Alarm"))
        assert alarm.enabled is False

    def test_name_stripped_of_disabled_prefix(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISABLED] Morning Alarm"))
        assert alarm.name == "Morning Alarm"

    def test_state_remains_before(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISABLED] Morning Alarm"))
        assert alarm.state == "before"


# ---------------------------------------------------------------------------
# RRULE repeat modes
# ---------------------------------------------------------------------------


class TestRruleRepeat:
    def test_daily(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm", rrule="FREQ=DAILY"))
        assert alarm.repeat == "daily"

    def test_weekdays(self) -> None:
        alarm = Alarm.from_calendar_event(
            make_event("Alarm", rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR")
        )
        assert alarm.repeat == "weekdays"

    def test_weekends(self) -> None:
        alarm = Alarm.from_calendar_event(
            make_event("Alarm", rrule="FREQ=WEEKLY;BYDAY=SA,SU")
        )
        assert alarm.repeat == "weekends"

    def test_weekly(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm", rrule="FREQ=WEEKLY"))
        assert alarm.repeat == "weekly"

    def test_custom_rrule_stored_verbatim(self) -> None:
        custom = "FREQ=MONTHLY;BYDAY=1MO"
        alarm = Alarm.from_calendar_event(make_event("Alarm", rrule=custom))
        assert alarm.repeat == custom


# ---------------------------------------------------------------------------
# base_id and is_snooze properties
# ---------------------------------------------------------------------------


class TestAlarmProperties:
    def test_base_id_without_snooze(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm", uid="my-base"))
        assert alarm.base_id == "my-base"

    def test_base_id_strips_snooze_suffix(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 2] Alarm", uid="my-base"))
        assert alarm.base_id == "my-base"

    def test_is_snooze_false_for_original(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Alarm"))
        assert alarm.is_snooze is False

    def test_is_snooze_true_for_snooze_1(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 1] Alarm"))
        assert alarm.is_snooze is True

    def test_is_snooze_true_for_snooze_3(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[SNOOZE 3] Alarm"))
        assert alarm.is_snooze is True


# ---------------------------------------------------------------------------
# to_dict serialisation
# ---------------------------------------------------------------------------


class TestToDict:
    REQUIRED_KEYS = (
        "id",
        "name",
        "time",
        "enabled",
        "repeat",
        "snooze_count",
        "timeout",
        "max_snoozes",
        "snooze_duration",
        "state",
        "next_snooze_time",
    )

    def test_contains_all_required_keys(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("Test Alarm"))
        d = alarm.to_dict()
        for key in self.REQUIRED_KEYS:
            assert key in d, f"Missing key in to_dict(): {key}"

    def test_name_matches(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("My Alarm"))
        assert alarm.to_dict()["name"] == "My Alarm"

    def test_state_matches(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("[DISMISSED] My Alarm"))
        assert alarm.to_dict()["state"] == "dismissed"

    def test_time_is_iso_string_or_none(self) -> None:
        alarm = Alarm.from_calendar_event(make_event("My Alarm"))
        t = alarm.to_dict()["time"]
        # Should be a non-empty ISO string
        assert isinstance(t, str)
        assert "T" in t or "-" in t
