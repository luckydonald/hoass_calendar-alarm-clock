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

It is an integration, multiple can be setup, each attached to their own calender.
I would assume the following flow:
- Add integration
- Choose calendar to load/save events to
- Setup defaults (snooze, timeout)

If a calender is set up in home assistant, I want automatic discovery for that, offering me to add that integration.

Write me the code for this plugin.

—————————

Make a markdown file in the ai folder, outlining what to do in detail.

————————

It shall be in vue, and you're missing the non-list view in the lovelace frontend.
Create ai/progress.md, and keep it updated when you complete steps.
After creating that file, start implementing!

—————————

use yarn, vue 3 <script setup lang="ts">, typescript, full types in python 3.12.
UV is nice, I wanna use that.

—————————

ALWAYS keep ai/progress.md, ai/overview.md updated with the current state of the project!

——————————

Never use `rm -f`, always use safer alternatives (e.g. interactive).

———————————

I want proper typing, don't just disable it.

———————————

The project is named **Calendar backed Alarm Clock for Home Assistant**.

The repo is at https://github.com/luckydonald/hoass_calendar-alarm-clock/tree/mane

———————————

Have the build happen on a github pipeline, building releases made for hacs.

———————————

Make sure to use best practices for home assistant plugins.
This includes using async where possible, proper config flows, etc.
Also this means reusing `<ha-icon>`, `<ha-card>`, etc. where possible.

———————————

The "Ringing alarm" kind of display is missing.
Remember, there needs to be the included buttons to take action.

———————————

The list panel doesn't really list any more than one alarm. Have it similar to typical modern phone alarm listings, including a svg of a clock displaying the time dynamically, including day/night visually.
Also it currently only shows a time, but not the day.


Also add a quick alarm command, which sets an alarm in a given time (30 minutes, 1h, 6h, custom) i.e. for a quick nap or so. This should trigger a event so other stuff can listen to it.
Modify the panel in the following way:
- include calendar in its name
- Have toggable sections
- Also create a big clock of current time on top,
    - Current time, analog/24h/12h
    - Active alarm indicator with the day and time (red = within 12h, yellow=anywhere in the future)
    - Add alarm button, opens config flow or something
- List of alarms
    - The default is to show a list of all alarms for the next 7days,
        - but you can configure either x time
        - or y alarms (count)
- Section to add a alarm (name, time, etc. (This is alrealdy implemented, but this section should be optional, allowing On and Off (to always show/hide it), as well as automatic, which shows it if you clicked on [add element]

——————

Rename `Calender Alarm Clock Card` to `Calendar Alarm Clock Card` everywhere.
Make sure the custom components are named `calender-alarm-clock-card` and `calender-alarm-clock-editor`
