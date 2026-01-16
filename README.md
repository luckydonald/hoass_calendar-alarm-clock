# Calendar backed Alarm Clock for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/luckydonald/hoass_calendar-alarm-clock.svg)](https://github.com/luckydonald/hoass_calendar-alarm-clock/releases)
[![CI](https://github.com/luckydonald/hoass_calendar-alarm-clock/actions/workflows/ci.yml/badge.svg)](https://github.com/luckydonald/hoass_calendar-alarm-clock/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/luckydonald/hoass_calendar-alarm-clock.svg)](LICENSE)

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

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=luckydonald&repository=hoass_calendar-alarm-clock&category=integration)

Or manually:

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/luckydonald/hoass_calendar-alarm-clock` and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/luckydonald/hoass_calendar-alarm-clock/releases)
2. Copy the `custom_components/calendar_alarm_clock` folder to your `custom_components` directory
3. Copy `custom_components/calendar_alarm_clock/www/alarm-clock-card.js` to your `www` folder
4. Restart Home Assistant

## Configuration

### Automatic Discovery
When you set up a calendar integration (like CalDAV or Google Calendar), the Alarm Clock integration will automatically be suggested in your notifications. Simply click to configure it.

### Manual Setup
1. Go to Settings → Devices & Services → Add Integration
2. Search for "Calendar backed Alarm Clock"
3. Select the calendar entity to use for storing alarms
4. Configure default settings via the integration options:
   - **Snooze duration** (default: 9 minutes)
   - **Alarm timeout** (default: 30 minutes)
   - **Max snoozes** (default: 3, set to 0 for infinite)

## Lovelace Card

Add the card resource to your Lovelace configuration:

```yaml
resources:
  - url: /local/alarm-clock-card.js
    type: module
```

Or if using HACS, it will be automatically added.

### Card Configuration

**List View** (default - shows all alarms):
```yaml
type: custom:alarm-clock-card
title: My Alarms
```

**Single Alarm View** (shows one specific alarm):
```yaml
type: custom:calender-alarm-clock-card
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
yarn install
yarn build
```

The built file will be placed in `custom_components/calendar_alarm_clock/www/`.

## Development

### Frontend
- Vue 3 with `<script setup lang="ts">`
- TypeScript
- Vite for bundling
- Yarn as package manager

### Backend
- Python 3.12 with full type annotations
- Home Assistant custom component

### CI/CD
Releases are built automatically via GitHub Actions:
- Push a tag like `v1.0.0` to create a release
- The frontend is built and bundled
- A release zip is created and published to GitHub Releases
- HACS will automatically pick up new releases

## Development Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 22+
- Yarn

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/luckydonald/hoass_calendar-alarm-clock.git
cd hoass_calendar-alarm-clock

# Set up everything (Python deps + frontend)
make setup

# Or manually:
uv sync
cd frontend && yarn install
```

### Running Linters

```bash
# Python: Check for lint issues
uv run ruff check custom_components/

# Python: Auto-fix lint issues
uv run ruff check --fix custom_components/

# Python: Format code
uv run ruff format custom_components/

# Python: Check formatting (without changing)
uv run ruff format --check custom_components/

# Frontend: Type check
cd frontend
yarn type-check
```

### Building

```bash
# Build frontend
cd frontend
yarn build

# The built JS file is placed in custom_components/calendar_alarm_clock/www/
```

### Testing Locally

1. Copy `custom_components/calendar_alarm_clock` to your Home Assistant's `custom_components/` folder
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services

### Creating a Release

The easiest way to create a release is using the release script:

```bash
# One command to: bump version, lint, format, build, commit, tag, and push
make release
```

This will:
1. Bump the version (e.g., `v0.0.0-pre11` → `v0.0.0-pre12`)
2. Lint and format Python code with ruff
3. Type-check and build the frontend
4. Commit, tag, and push to GitHub

Alternatively, do it manually:

```bash
# Lint and format
make lint
make format

# Build
make build

# Commit and tag
git add .
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin mane
git push origin vX.Y.Z
```

### Make Commands

```bash
make help     # Show all available commands
make setup    # Set up development environment
make lint     # Run all linters
make format   # Format all code
make build    # Build frontend
make release  # Full release workflow
```

## Links

- [GitHub Repository](https://github.com/luckydonald/hoass_calendar-alarm-clock)
- [Issue Tracker](https://github.com/luckydonald/hoass_calendar-alarm-clock/issues)
- [Releases](https://github.com/luckydonald/hoass_calendar-alarm-clock/releases)

## License

MIT License

