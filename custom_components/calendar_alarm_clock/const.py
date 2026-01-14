"""Constants for Calendar Alarm Clock."""
from typing import Final

DOMAIN: Final = "calendar_alarm_clock"

# Configuration keys
CONF_CALENDAR_ENTITY: Final = "calendar_entity"
CONF_DEFAULT_SNOOZE_DURATION: Final = "default_snooze_duration"
CONF_DEFAULT_ALARM_TIMEOUT: Final = "default_alarm_timeout"
CONF_DEFAULT_MAX_SNOOZES: Final = "default_max_snoozes"
CONF_DEFAULT_REPEAT: Final = "default_repeat"

# Default values
DEFAULT_NAME: Final = "Alarm"
DEFAULT_SNOOZE_DURATION: Final = 9  # minutes
DEFAULT_ALARM_TIMEOUT: Final = 30.0  # minutes
DEFAULT_MAX_SNOOZES: Final = 3
DEFAULT_REPEAT: Final = "none"  # none, daily, weekdays, weekends, weekly, custom

# Alarm states
STATE_BEFORE: Final = "before"
STATE_RINGING: Final = "ringing"
STATE_SNOOZED: Final = "snoozed"
STATE_DISMISSED: Final = "dismissed"
STATE_RINGING_SNOOZE: Final = "ringing_snooze"
STATE_TIMED_OUT: Final = "timed_out"

ALARM_STATES: Final = [
    STATE_BEFORE,
    STATE_RINGING,
    STATE_SNOOZED,
    STATE_DISMISSED,
    STATE_RINGING_SNOOZE,
    STATE_TIMED_OUT,
]

# Event types
EVENT_ALARM_RINGING: Final = f"{DOMAIN}.alarm_ringing"
EVENT_ALARM_SNOOZED: Final = f"{DOMAIN}.alarm_snoozed"
EVENT_ALARM_DISMISSED: Final = f"{DOMAIN}.alarm_dismissed"
EVENT_ALARM_TIMED_OUT: Final = f"{DOMAIN}.alarm_timed_out"
EVENT_ALARM_CREATED: Final = f"{DOMAIN}.alarm_created"
EVENT_ALARM_DELETED: Final = f"{DOMAIN}.alarm_deleted"
EVENT_ALARM_EDITED: Final = f"{DOMAIN}.alarm_edited"
EVENT_ALARM_ENABLED: Final = f"{DOMAIN}.alarm_enabled"
EVENT_ALARM_DISABLED: Final = f"{DOMAIN}.alarm_disabled"

# Prefixes for calendar events
PREFIX_SNOOZE: Final = "[SNOOZE {}] "
PREFIX_DISMISSED: Final = "[DISMISSED] "
PREFIX_DISABLED: Final = "[DISABLED] "
SUFFIX_SNOOZE: Final = "-snooze-{}"

# Attributes
ATTR_ALARM_ID: Final = "alarm_id"
ATTR_NAME: Final = "name"
ATTR_TIME: Final = "time"
ATTR_ENABLED: Final = "enabled"
ATTR_REPEAT: Final = "repeat"
ATTR_NEXT_SNOOZE_TIME: Final = "next_snooze_time"
ATTR_SNOOZE_COUNT: Final = "snooze_count"
ATTR_TIMEOUT: Final = "timeout"
ATTR_MAX_SNOOZES: Final = "max_snoozes"
ATTR_SNOOZE_DURATION: Final = "snooze_duration"

# Service names
SERVICE_CREATE_ALARM: Final = "create_alarm"
SERVICE_DELETE_ALARM: Final = "delete_alarm"
SERVICE_ENABLE_ALARM: Final = "enable_alarm"
SERVICE_DISABLE_ALARM: Final = "disable_alarm"
SERVICE_LIST_ALARMS: Final = "list_alarms"
SERVICE_EDIT_ALARM: Final = "edit_alarm"
SERVICE_TRIGGER_ALARM: Final = "trigger_alarm"
SERVICE_SNOOZE_ALARM: Final = "snooze_alarm"
SERVICE_DISMISS_ALARM: Final = "dismiss_alarm"

# Platforms
PLATFORMS: Final = ["sensor"]

# Update interval (seconds)
UPDATE_INTERVAL: Final = 30

