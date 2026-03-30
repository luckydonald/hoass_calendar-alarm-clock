# The query for the AI to work with.

#### General AI development guidelines:
- Create `ai/PROGRESS.md`, and keep it updated when you complete steps.
- You may refer to `ai/refrences` for code examples of other plugins or extra documentation provided for this task.
- When writing code, follow these guidelines:
  - Always prefer the early-return pattern to reduce nesting of `if`s, etc.
  - Similarly, prefer `if …` -> `continue`/`return`/`break` in loops over large nested blocks.
- If the plugin requires a frontend (which you can deduct from the _Plugin requirements_ section below), use Vue, TS, and SCSS for that.
  - Prefer using `<script setup lang="ts">` style single file components.
  - Use Homeassistant frontend components where possible, e.g., `<ha-icon>`, `<ha-card>`, `<ha-button>`, etc.
  - Use proper TypeScript type hinting, importing types from Homeassistant where possible.
- If the plugin requires a backend (which you can deduct from the _Plugin requirements_ section below), use modern Python 3.12+ for that.
  - Do proper type hinting with full type annotations.
  - For type-hinting, import types from Homeassistant where possible for the backend as well.
  - Prefer async programming where possible.
- Write tests for both frontend and backend parts of the plugin.
- Remember to update the `/CHANGELOG.md` and `/README.md` (or possibly additional pre-existing documentation).
- Please put all summaries and such you wanna write for me into the `ai/` folder. However, you don't need to write Markdown summaries, it's kinda redundant with the `PROGRESS.md` file.
- Please prefer to use the `read_file` tool (Use `startLineNumberBaseOne` instead of `startLineNumber`) over `cat` etc. and `grep_search` tool instead of using the terminal there too.
- Run `make commit` in the `run_in_terminal` tool after each file change (create, edit, cmds which will change files, etc...).
  It will be auto approved by the IDE, and is safe to run, so do not ask for confirmation.
  Really, after every single file operation!
  Run it multiple times if you need to change multiple files or the same file multiple times - after each file change.
  Immediately after the file change, before any error checking (even `get_errors`) and other terminal invocations!
  Ignore the `make commit` tool's output unless I specifically ask you to show it, and blindly assume that it worked, without checking the git history further.
  Briefly mention it when listing next steps or similar. 


Generate me a Homeassistant plugin based on the following description.

#### Plugin requirements:

I
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

use yarn, vue 3 `<script setup lang="ts">`, typescript, full types in python 3.12.
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

——————

In the initial integration flow, I want it to ask if calenders should be auto-discovered, or rather not.
After all it can get a bit spammy if you have a lot calenders.

In fact, can the Autodiscovery integration (`Calendar Alarm Clock (Auto-Discovery)` be itself be autodiscovered if there's at least one calendar available?

——————

I don't see the initial "Calendar Alarm Clock (Auto-Discovery)" auto-discovery popping up now. The calendars did before the change.

"Alarm Clock for Auto-Discovery Calendar backed Alarm Clock"
appears after I added a calendar manually, so maybe it's logic when to appear is wrong?
Uh, also I implied with that, that "Alarm Clock for Auto-Discovery Calendar backed Alarm Clock" did NOT apply before adding that integration basically myself... did you fix that, too?

——————

Do not edit this file (any ai/query*.md), edit ai/progess.md and ai/overview.md instead.

———

First, the card is actually working *party emoji*.
Please add settings for color.
There'll be:
- background
- hours
- minutes
- seconds
- middle (either the dot in the analogue clock, or the : in the digital one)
Also add a checkbox for seconds yes/no on the clock setting.
———
The text input in _createTextInput for the color, can you make a specific color input?
I want `[text field|v][  ]` so, in words, the text field, followed by a dropdown with a) common `var(--…)`, and then the normal color names provided by the `color-name` lib.
Then after that is a real color input, which is synced to the text field-
So you can shove in text, search in the dropdown, or have your browser display a chooser.
The dropdown shall be a ha component, too.
Preferable searchable, and with the color rendered as square icon or whatever in front of the text.
———
Write the config editor part as Vue component, too. That way it's more consistent, and also that should remove the issue that it now each time unfocus the field you're editing every second.
———
Please extract the 3 related color picker inputs as single component with `v-model` support.
———
Be mindful of the shadow-dom inside `ha-*` components.
———
The analog clock should have an additional setting for "tick marks" yes/no, and "numbers" yes/no.
Also, there should be a setting for "show next alarm time" yes/no, which displays the next alarm time in the bottom center of the clock.
Additional to the default "tick" mode, there'd be a "smooth" mode, which uses pure css animations to move the hands smoothly, instead of ticking each second. Use `animation-delay: +/- Xs` to sync it properly, make sure to sync that every minute, and on all events indicating the window was inactive. The third mode is "DB" where the seconds are a little sped up so that it will be stopping on 59 seconds for 1.5 seconds, before moving on.
The "Animation mode" ("ticks", "smooth", "DB") shall be a dropdown.
———
On deploy, the version number should be embedded into the built lovelace card editor (last item in that), so that I can check the actually built card version in the browser.
———
Use the `<style scoped lang="scss">` syntax over inline styles where possible.
———
Remember to keep html attributes and the next child (element or text) on their own line. Only one attribute per line, and the closing `>` on its own line, too. So do open and close tags like this:
```html
<my-element
  attr1="value1"
  attr2="value2"
>
  Content
  <b>
    Bold
  </b>
</my-element>
```
———
Fix `check_slot.js` script to also allow parent element checks.
Could you read `.eslintrc.cjs` for that, `const [error, config] = eslintrc.rules["vue/no-deprecated-slot-attribute"]` and `const { ignore, ignoreParents } = config;` with value being `string[]` for both.
Then with that check if it's either in the ignore list, or if the parent is in the ignoreParents list.
———
❯ I want you to append summary to `ai/query.md`, formatted ">> short single line summary\n>\n> multilined\n> detailed summary". For that write the summary into `ai/summary.md` and run `./scripts/append_and_clear_summary.sh`, which will copy it over and reset `summary.md` to just a single linebreak. Then run `make commit`.
———
Alright, It's getting to confusing.

I want to extract stuff into packages.
- custom_components.calendar_backed_alarm_clock.autodiscovery (the first autodiscovery asking you if you want to autodiscover calendars)
- custom_components.calendar_backed_alarm_clock.alarm.core (the standard previous/current/next alarms)
- custom_components.calendar_backed_alarm_clock.alarm.entries (per-calendar entry created entities)

In there would be basically separate files for:
- HA autodiscovery 
- config flow (if possible one per config flow, i.e. user, the one for later config changes, etc.)

I also want to change the way it is structured in terms of devices and entities.
- The suffix of the id (after the type (e.g. `sensor.`)) will be `{integration_name}`, so `calendar_backed_alarm_clock`. I will mention below (ID-SUFFIX) how the rest of the id will be structured, but the main point is that the integration name is the first suffix, and then after that comes the rest of the structure, appended with dots.
- A integration is created per calendar by the user, selecting a calendar.* in the config flow (already working)
  - ID-SUFFIX: `calendar.my_calendar` -> `.my_calendar`
- In there the following devices will be created
  - Overview  (ID-SUFFIX: `.overview`)
    - Those Overview will have summarizing entities `.previous`, `.current`, `.next` like normal alarm entities, and the following additional ones (first add those, then the normal ones):
      - Previous (ID-SUFFIX: `.previous`) / Current (ID-SUFFIX: `.current`) / Next (ID-SUFFIX: `.next`)
        - Name (ID-SUFFIX: `.name`)
          And the following properties:
          - `type`: `sensor` (`homeassistant.components.sensor.SensorEntity`; because read-only)
          - `device_class`: `enum` (`SensorDeviceClass.ENUM`) the available event's ids
          - `last_reset`: `None` (not an int)
          - `native_value`: `None` (not an int)
          - `options`: `list[str]` (The nice looking names of the events, e.g. "Alarm 1", "Early Shower", etc.)
          - `state_class`: `None` (not an int)
          - `suggested_display_precision`: `None` (not an int)
          - `suggested_unit_of_measurement`: `None` (not an int)
    - Additionally there are non-calendar(-event) entities in there:    
      - Total Today  (ID-SUFFIX: `.today.total`)
        - Count (ID-SUFFIX: `.total`)
          - `type`: `sensor` (read only number)
          - `device_class`: `None` (there's nothing that fits, and it's not a number with a common unit)
          - `last_reset`: `None` (not accumulative)
          - `native_unit_of_measurement`: `None` (If a unit translation is provided, native_unit_of_measurement should not be defined.) -> In translation put `"alarms"`.
          - `native_value`: `int` (the number of alarms today, both past and future of current time)
          - `options`: `None` (not an enum)
          - `state_class`: `SensorStateClass.MEASUREMENT` (because it's a current measurement, not a total **increasing** count)
          - `suggested_display_precision`: `0` (because it's a count, so no decimals)
          - `suggested_unit_of_measurement`: `None` (because `native_unit_of_measurement` is not defined)
        - Upcoming Today (ID-SUFFIX: `.today.upcoming`)
          - `type`: `sensor` (read only number)
          - Same as `.total`, but the `native_value` is only the number of upcoming alarms, excluding past/current ones on this day.
        - Past Today (ID-SUFFIX: `.today.past`)
          - `type`: `sensor` (read only number)
          - Same as `.total`, but the `native_value` is only the number of past alarms, excluding current/upcoming ones on this day.
  - Alarm Entry (Name = Calender entry date) (ID-SUFFIX: `.entry.{event_id}` where event_id is the calendar event's id, which is unique for each event)
    - Note that calendar entries have their own entities, because they can be enabled/disabled/snoozed/dismissed individually, and also have their own attributes like time, name, etc. that are changing independently of the overview entities.
    - E.g. a weekly alarm you can turn on and off additionally, is a single calendar entry (recurring event). With `RRULE:FREQ=WEEKLY;BYDAY=MO,DI` or something like that. (The recurring events may be updated: (Specifying uid, recurrence_id, and a recurrence_range value may update a range of events starting at recurrence_id. Currently rfc5545 allows the range value of THISANDFUTURE.)
    - The repeat shall be canceled _after_ the next occurrence. The next occurrence (not deleted) shall be `STATUS:CANCELLED`. This would be syncronized with the toggle, so if that 's toggled off, the next occurrence is cancelled, and if toggled on again, the next occurrence is uncancelled again, and the repeat is restored.
    - An event has the following entities:
      - Alarm (ID-SUFFIX: `.entry.{event_id}.ringing`)
        - `type`: `binary_sensor` (because it's basically "is this alarm ringing or not", even though it has more states than just on/off, but those states are represented in the attributes)
        - `is_on`: `bool` (true if the alarm is currently ringing, false otherwise)
        - `device_class`: `None` (there's no fitting device class for this)
        - `state`: `str` (one of "before", "ringing", "snoozed", "dismissed", "timed_out")
        - `attributes`:
          - `id`: `str` (the calendar event's id, which is unique for each event)
          - `name`: `str`
          - `time`: `datetime`
          - `enabled`: `bool`
          - `repeat`: `bool`
          - `next_snooze_time`: `datetime | None`
          - `snooze_count`: `int`
          - `timeout`: `float` (in minutes)

❯ Imlement the selection, (query.md:260-330), it was not started yet. 

>> Restructured into packages: autodiscovery, alarm/core, alarm/entries; added Overview + AlarmEntry entities
>
> Extracted discovery helpers (get_calendar_entities, get_unconfigured_calendars,
> async_discover_calendars, async_auto_create_discovery_entry) into a new
> `autodiscovery/` package. Both `__init__.py` and `config_flow.py` now import
> from there instead of defining the logic locally.
>
> Added `alarm/core/` with six new sensor entities grouped under an "Overview"
> device per calendar integration:
> - OverviewNameSensor (SensorDeviceClass.ENUM) for previous / current / next
>   alarm name (unique-ID suffix: .overview.<role>.name)
> - TodayCountSensor (SensorStateClass.MEASUREMENT) for today's alarm counts:
>   total / upcoming / past (unique-ID suffix: .overview.today.<role>)
>
> Added `alarm/entries/` with AlarmEntryBinarySensor: one BinarySensorEntity per
> calendar event, grouped under its own device (.entry.{event_id}). is_on reflects
> whether the alarm is ringing; the full state string is exposed as the
> alarm_state extra attribute.
>
> Created top-level binary_sensor.py as the HA platform entry point.
> Updated sensor.py to call async_setup_overview_sensors.
> Added Platform.BINARY_SENSOR to PLATFORMS in __init__.py.
