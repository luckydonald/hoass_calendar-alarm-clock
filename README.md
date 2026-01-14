# Calendar Alarm Clock

A Home Assistant custom component that provides phone-like alarm clock functionality, storing alarms in your CalDAV calendar.

## Features

- 📅 **Calendar-based storage**: Alarms are stored as calendar events in your CalDAV calendar
- 🔁 **Recurring alarms**: Support for daily, weekday, weekend, and weekly repeat patterns
- 😴 **Snooze support**: Configurable snooze duration and maximum snoozes
- ⏰ **Alarm timeout**: Automatic timeout for unattended alarms
- 🔔 **Notifications**: Persistent notifications when alarms ring
- 🎴 **Lovelace Card**: Beautiful Vue.js card for managing alarms
- 🏠 **Home Assistant native**: Full integration with HA events, services, and automations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/calendar_alarm_clock` folder to your `custom_components` directory
2. Copy `custom_components/calendar_alarm_clock/www/alarm-clock-card.js` to your `www` folder
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Calendar Alarm Clock"
3. Select the calendar entity to use for storing alarms
4. Configure default settings (snooze duration, timeout, max snoozes)

## Lovelace Card

Add the card resource to your Lovelace configuration:

```yaml
resources:
  - url: /local/alarm-clock-card.js
    type: module
```

Or if using HACS, it will be automatically added.

### Card Configuration

```yaml
type: custom:alarm-clock-card
title: My Alarms
```

For a single alarm view (showing one specific alarm):

```yaml
type: custom:alarm-clock-card
entity: sensor.alarm_clock_abc123
title: Wake Up Alarm
```

## Services

### `calendar_alarm_clock.create_alarm`

Create a new alarm.

| Field | Description | Required | Default |
|-------|-------------|----------|---------|
| `name` | Alarm name | No | "Alarm" |
| `time` | Time (HH:MM) | No | Current time |
| `date` | Date (YYYY-MM-DD) | No | Today |
| `repeat` | Repeat pattern | No | "none" |
| `enabled` | Enable alarm | No | true |

### `calendar_alarm_clock.delete_alarm`

Delete an alarm.

| Field | Description |
|-------|-------------|
| `entity_id` | Alarm entity ID |
| `alarm_id` | Alarm ID |

### `calendar_alarm_clock.snooze_alarm`

Snooze a ringing alarm.

| Field | Description |
|-------|-------------|
| `entity_id` | Alarm entity ID |
| `alarm_id` | Alarm ID |
| `duration` | Snooze duration (minutes) |

### `calendar_alarm_clock.dismiss_alarm`

Dismiss a ringing alarm.

| Field | Description |
|-------|-------------|
| `entity_id` | Alarm entity ID |
| `alarm_id` | Alarm ID |

### `calendar_alarm_clock.enable_alarm` / `disable_alarm`

Enable or disable an alarm.

### `calendar_alarm_clock.edit_alarm`

Edit an existing alarm.

### `calendar_alarm_clock.trigger_alarm`

Manually trigger an alarm (for testing).

### `calendar_alarm_clock.list_alarms`

List all alarms.

## Events

The integration fires the following events:

- `calendar_alarm_clock.alarm_ringing` - Alarm started ringing
- `calendar_alarm_clock.alarm_snoozed` - Alarm was snoozed
- `calendar_alarm_clock.alarm_dismissed` - Alarm was dismissed
- `calendar_alarm_clock.alarm_timed_out` - Alarm timed out
- `calendar_alarm_clock.alarm_created` - New alarm created
- `calendar_alarm_clock.alarm_deleted` - Alarm deleted
- `calendar_alarm_clock.alarm_edited` - Alarm edited
- `calendar_alarm_clock.alarm_enabled` - Alarm enabled
- `calendar_alarm_clock.alarm_disabled` - Alarm disabled

## Entities

Each alarm creates a sensor entity with the following attributes:

- `alarm_id` - Unique alarm identifier
- `name` - Alarm name
- `time` - Alarm time (ISO format)
- `enabled` - Whether alarm is enabled
- `repeat` - Repeat pattern
- `snooze_count` - Number of times snoozed
- `timeout` - Timeout duration
- `max_snoozes` - Maximum allowed snoozes

Global sensors:
- `sensor.<entry>_next_alarm` - Next upcoming alarm
- `sensor.<entry>_previous_alarm` - Most recent alarm

## Alarm States

- `before` - Alarm is scheduled, waiting to ring
- `ringing` - Alarm is currently ringing
- `ringing_snooze` - Snoozed alarm is ringing again
- `snoozed` - Alarm has been snoozed
- `dismissed` - Alarm has been dismissed
- `timed_out` - Alarm timed out without being dismissed

## Example Automations

### Play sound when alarm rings

```yaml
automation:
  - alias: "Play alarm sound"
    trigger:
      - platform: event
        event_type: calendar_alarm_clock.alarm_ringing
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.bedroom_speaker
        data:
          media_content_id: /local/alarm.mp3
          media_content_type: music
```

### Turn on lights when alarm rings

```yaml
automation:
  - alias: "Turn on bedroom lights for alarm"
    trigger:
      - platform: event
        event_type: calendar_alarm_clock.alarm_ringing
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 100
          transition: 30
```

## Building the Frontend

If you want to modify the frontend:

```bash
cd frontend
npm install
npm run build
```

The built file will be placed in `custom_components/calendar_alarm_clock/www/`.

## License

MIT License

