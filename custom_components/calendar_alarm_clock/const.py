"""Constants for Calendar Alarm Clock."""

import json
from pathlib import Path
from typing import Final, Literal

from homeassistant.loader import Manifest

DIR = Path(__file__).parent
MANIFEST_FILE = DIR / "manifest.json"

with open(MANIFEST_FILE) as f:
    MANIFEST_DATA: Manifest = json.load(f)
# end if

DOMAIN: Final[str] = "calendar_alarm_clock"
"""Constants for this plugin."""

# DOMAIN: Final[str] = MANIFEST_DATA["domain"]
LOG_NAME: Final[str] = f"custom-components.{DOMAIN}"

# Configuration keys
CONF_CALENDAR_ENTITY: Final[str] = "calendar_entity"
CONF_AUTO_DISCOVER_CALENDARS: Final[str] = "auto_discover_calendars"
CONF_DEFAULT_SNOOZE_DURATION: Final[str] = "default_snooze_duration"
CONF_DEFAULT_ALARM_TIMEOUT: Final[str] = "default_alarm_timeout"
CONF_DEFAULT_MAX_SNOOZES: Final[str] = "default_max_snoozes"
CONF_DEFAULT_REPEAT: Final[str] = "default_repeat"

# Default values
DEFAULT_NAME: Final[str] = "Alarm"
DEFAULT_SNOOZE_DURATION: Final[int] = 9  # minutes
DEFAULT_ALARM_TIMEOUT: Final[float] = 30.0  # minutes
DEFAULT_MAX_SNOOZES: Final[int] = 3
DEFAULT_REPEAT: Final[str] = "none"  # none, daily, weekdays, weekends, weekly, custom

# Alarm states
STATE_BEFORE: Final[str] = "before"
STATE_RINGING: Final[str] = "ringing"
STATE_SNOOZED: Final[str] = "snoozed"
STATE_DISMISSED: Final[str] = "dismissed"
STATE_RINGING_SNOOZE: Final[str] = "ringing_snooze"
STATE_TIMED_OUT: Final[str] = "timed_out"

AlarmState = Literal["before", "ringing", "snoozed", "dismissed", "ringing_snooze", "timed_out"]

ALARM_STATES: Final[list[AlarmState]] = [
    "before",
    "ringing",
    "snoozed",
    "dismissed",
    "ringing_snooze",
    "timed_out",
]

# Event types
EVENT_ALARM_RINGING: Final[str] = f"{DOMAIN}.alarm_ringing"
EVENT_ALARM_SNOOZED: Final[str] = f"{DOMAIN}.alarm_snoozed"
EVENT_ALARM_DISMISSED: Final[str] = f"{DOMAIN}.alarm_dismissed"
EVENT_ALARM_TIMED_OUT: Final[str] = f"{DOMAIN}.alarm_timed_out"
EVENT_ALARM_CREATED: Final[str] = f"{DOMAIN}.alarm_created"
EVENT_ALARM_DELETED: Final[str] = f"{DOMAIN}.alarm_deleted"
EVENT_ALARM_EDITED: Final[str] = f"{DOMAIN}.alarm_edited"
EVENT_ALARM_ENABLED: Final[str] = f"{DOMAIN}.alarm_enabled"
EVENT_ALARM_DISABLED: Final[str] = f"{DOMAIN}.alarm_disabled"

# Prefixes for calendar events
PREFIX_SNOOZE: Final[str] = "[SNOOZE {}] "
PREFIX_DISMISSED: Final[str] = "[DISMISSED] "
PREFIX_DISABLED: Final[str] = "[DISABLED] "
SUFFIX_SNOOZE: Final[str] = "-snooze-{}"

# Attributes
ATTR_ALARM_ID: Final[str] = "alarm_id"
ATTR_NAME: Final[str] = "name"
ATTR_TIME: Final[str] = "time"
ATTR_ENABLED: Final[str] = "enabled"
ATTR_REPEAT: Final[str] = "repeat"
ATTR_NEXT_SNOOZE_TIME: Final[str] = "next_snooze_time"
ATTR_SNOOZE_COUNT: Final[str] = "snooze_count"
ATTR_TIMEOUT: Final[str] = "timeout"
ATTR_MAX_SNOOZES: Final[str] = "max_snoozes"
ATTR_SNOOZE_DURATION: Final[str] = "snooze_duration"

# Service names
SERVICE_CREATE_ALARM: Final[str] = "create_alarm"
SERVICE_DELETE_ALARM: Final[str] = "delete_alarm"
SERVICE_ENABLE_ALARM: Final[str] = "enable_alarm"
SERVICE_DISABLE_ALARM: Final[str] = "disable_alarm"
SERVICE_LIST_ALARMS: Final[str] = "list_alarms"
SERVICE_EDIT_ALARM: Final[str] = "edit_alarm"
SERVICE_TRIGGER_ALARM: Final[str] = "trigger_alarm"
SERVICE_SNOOZE_ALARM: Final[str] = "snooze_alarm"
SERVICE_DISMISS_ALARM: Final[str] = "dismiss_alarm"

# Platforms
PLATFORMS: Final[list[str]] = ["sensor"]

# Update interval (seconds)
UPDATE_INTERVAL: Final[int] = 30
