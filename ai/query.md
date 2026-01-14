 want to create a homeassistent plugin (HACS), which provides me the abilitity to schedule alarm clocks, as one would on a phone.
That means:
- name (default = "Alarm")
- enabled (default = true)
- time, day
- repeat? (unset = global set default)
- max snoozes (unset = global set default; null = infinite)
- alarm timeout (in minutes, float, unset = global set default)

Additionally, when the alarm rings, I want to be able to:
- snooze it (for x minutes, unset = global set default)
- dismiss it


It shall come with a lovelace panel to display and edit alarms:
- if a entity is set, show only that entity's alarms, else show all alarms
- listing all alarms (this week)
  - show alarm details (name, time, enabled, repeat, ...)
- disable/enable an alarm (toggle)
- edit alarm details (see above)
- add a new alarm (see above)
- delete a alarm
- display next alarm time in the header
- visually show when an alarm is ringing, a little shake animation on the alarm logo/icon would be nice

However those shall be stored in the CalDAV calender integration of homeassistant instead of being stored locally.

That means, an alarm every monday at 08:00 is actually just a reoccurring event on the calender chosen for the alarm.


When an alarm rings, a notification shall be created in homeassistant, with options to snooze or dismiss the alarm.

Snoozing an alarm means copying the event some minutes into the future with `[SNOOZE {i}] ` prefix, and dismissing it means editing `[DISMISSED] ` into the calender event (and set it and planned snoozes to free).
Have the id of the snoozed event be the original one with a `-snooze-{i}` suffix, so that the plugin can identify it as such.

The plugin shall provide the following services:
- create_alarm
- delete_alarm (entity, by name or id)
- enable_alarm (entity, by name or id)
- disable_alarm (entity, by name or id)
- list_alarms
- edit_alarm (entity, by name or id)
- trigger_alarm (for testing)
- snooze_alarm (entity, by name or id)
- dismiss_alarm (entity, by name or id)

Also entities for each alarm shall be created, so that automations can be build around them.
So each alarm is an entity of type `alarm_clock.alarm`, with attributes:
- id (base id from caldav event)
- name
- time
- enabled
- repeat
- next_snooze_time
- snooze_count (starts with 0 for original alarm, 1 for first snooze, etc)
- timeout
- state (before, ringing, dismissed, snoozed, ringing_snooze, timed_out)

The following events shall be fired:
- alarm_clock.alarm_ringing
- alarm_clock.alarm_snoozed
- alarm_clock.alarm_dismissed
- alarm_clock.alarm_timed_out
- alarm_clock.alarm_created
- alarm_clock.alarm_deleted
- alarm_clock.alarm_edited
- alarm_clock.alarm_enabled
- alarm_clock.alarm_disabled

There's also global next and previous entities, which represent the next and previous alarm in the system, with the same attributes events and functions as above.

When an alarm is ringing, the user shall be able to stop/snooze it via the notification, or via the entity (set state to snooze or dismissed).

Write me the code for this plugin.
