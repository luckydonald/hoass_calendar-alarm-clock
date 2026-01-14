# Implementation Plan: Calendar Alarm Clock (HACS Plugin)

## project Overview
A Home Assistant custom component that manages alarms using a CalDAV calendar as the storage backend. It includes entities for alarms, global next/previous alarm sensors, specific services, and a frontend interface.

## 1. Project Scaffolding
- **Directory**: `custom_components/calendar_alarm_clock/`
- **Files**:
    - `manifest.json`: Component metadata (domain: `calendar_alarm_clock`).
    - `__init__.py`: Component setup, service registration, platform forwarding.
    - `const.py`: Constants (Domain, defaults, event names).
    - `config_flow.py`: UI Configuration to select the target Calendar entity and set defaults.

## 2. Backend Logic (Python)

### A. Data Management (Calendar Interaction)
The core logic relies on the Home Assistant `calendar` entity.
- **Syncing**: Periodically fetch events from the selected calendar entity using `calendar.list_events` service.
- **Parsing**: Convert calendar events into "Alarm" objects.
    - **Reoccurring events**: Handled natively by the calendar, but we need to track the *next* occurrence.
    - **Snoozed events**: identified by `[SNOOZE {i}]` prefix and suffix ID `-snooze-{i}`.
    - **Dismissed events**: identified by `[DISMISSED]` in description or title? Prompt says "editing `[DISMISSED] ` into the calender event".

### B. Alarm State Machine
- **States**: `before`, `ringing`, `snoozed`, `dismissed`, `ringing_snooze`, `timed_out`.
- **Timer/Loop**: A background task (asyncio) checking every minute (or second) if an alarm time is reached.
- **State Transitions**:
    - `before` -> `ringing`: When `now() >= alarm_time`.
    - `ringing` -> `timed_out`: After `alarm_timeout` minutes.
    - `ringing` -> `snoozed`: Via service call. copy event to future.
    - `ringing` -> `dismissed`: Via service call. mark event dismissed.

### C. Entities
Since `alarm_clock` is not a standard HA domain, we will Register a new domain `alarm_clock` or use a `SensorEntity`/`SwitchEntity` with a custom device class.
*Given the requirement "entities of type `alarm_clock.alarm`", we will register entities under a custom domain.*

1.  **Alarm Entities** (`alarm_clock.alarm_ID`):
    - Represents individual alarms (based on calendar events).
    - Attributes: `name`, `time`, `enabled`, `repeat`, `next_snooze_time`, `snooze_count`, `timeout`, `state`.
    - Functionality: Toggle (enable/disable), which updates the calendar event (maybe prepends `[DISABLED]`).

2.  **Global Sensors**:
    - `sensor.next_alarm`: Attributes of the next upcoming alarm.
    - `sensor.previous_alarm`: Attributes of the last alarm.

### D. Services
Implement `services.py` to handle:
- `create_alarm(time, name, repeat, ...)` -> calls `calendar.create_event`.
- `delete_alarm(entity_id)` -> remove event.
- `snooze_alarm(entity_id, duration)` -> creates/updates snooze event.
- `dismiss_alarm(entity_id)` -> modifies event to dismissed status.
- `edit_alarm(...)`.
- `trigger_alarm(...)`.

### E. Events
Fire events on the bus `hass.bus.async_fire(...)`:
- `alarm_clock.alarm_ringing`
- `alarm_clock.alarm_snoozed`, etc.

### F. Notifications
- Detect `ringing` state transition.
- Call `notify.persistent_notification` or allow user to configure a notify service.
- Include action buttons (Snooze/Dismiss) in notification (requires mobile app notify service or persistent notification with actionable logic if possible, or simple text).

## 3. Frontend (Lovelace)
A custom Lovelace card (or panel) to manage alarms.
- **Micro-frontend**: Vue or LitElement based.
- **Features**:
    - List view of `alarm_clock` entities.
    - Add/Edit dialogs.
    - "Ringing" visual state (shake animation).
    - Header with next alarm.

## 4. Implementation Steps

1.  **Setup**: Create `custom_components/calendar_alarm_clock` and basic files.
2.  **Config Flow**: Allow selecting the `calendar.xyz` entity.
3.  **Alarm Manager**: Class to sync with calendar and hold state.
4.  **Entity Implementation**: Create the `AlarmClockEntity` class.
5.  **Service Implementation**: Map services to Manager methods.
6.  **Frontend**: Create a basic `alarm-clock-card.js`.

## 5. Notes / Assumptions
- The user has a working CalDAV calendar integrated into HA.
- We rely on `calendar.create_event` which supports recurrence rules.
- To "Edit" a recurring series exception (like dismissing one instance), we might need to create an exception event.
- Identification of "Alarm" events: We assume ALL events in the selected calendar are alarms.


