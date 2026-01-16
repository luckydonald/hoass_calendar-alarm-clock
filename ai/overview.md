# Calendar backed Alarm Clock for Home Assistant - Project Overview

**Repository**: https://github.com/luckydonald/hoass_calendar-alarm-clock

## Description
A Home Assistant custom component (HACS compatible) that provides phone-like alarm clock functionality, storing alarms in a CalDAV calendar.

## Setup Flow
1. **Automatic Discovery**: When a calendar integration is set up, this integration is automatically suggested
2. **Manual Setup**: Go to Settings → Devices & Services → Add Integration → "Calendar backed Alarm Clock"
3. **Select Calendar**: Choose which calendar to store alarms in
4. **Configure Options**: Set default snooze duration, timeout, max snoozes

## Architecture

### Backend (Python 3.12)
- **Domain**: `calendar_alarm_clock`
- **Storage**: CalDAV calendar events via Home Assistant's `calendar` integration
- **Auto-Discovery**: Listens for new calendar entities and offers setup
- **Components**:
  - `__init__.py` - Entry setup, platform forwarding, discovery listener
  - `config_flow.py` - UI configuration with auto-discovery support
  - `const.py` - Constants, types (using `Literal`, `Final`)
  - `models.py` - `Alarm` dataclass
  - `alarm_manager.py` - Core logic (sync, state machine, notifications)
  - `sensor.py` - Entity definitions
  - `services.py` - Service handlers

### Frontend (Vue 3 + TypeScript)
- **Framework**: Vue 3 with `<script setup lang="ts">`
- **Build**: Vite (bundled as IIFE web component)
- **Package Manager**: Yarn
- **Card Name**: `calender-alarm-clock-card`

## Alarm States
```
before → ringing → dismissed
              ↓
          snoozed → ringing_snooze → dismissed
              ↓                  ↓
          timed_out         timed_out
```

## Calendar Event Format
- **Normal**: `Alarm Name`
- **Disabled**: `[DISABLED] Alarm Name`
- **Snoozed**: `[SNOOZE 1] Alarm Name` (with `-snooze-1` ID suffix)
- **Dismissed**: `[DISMISSED] Alarm Name`

## Services
| Service | Description |
|---------|-------------|
| `create_alarm` | Create new alarm |
| `delete_alarm` | Delete alarm |
| `enable_alarm` | Enable alarm |
| `disable_alarm` | Disable alarm |
| `snooze_alarm` | Snooze ringing alarm |
| `dismiss_alarm` | Dismiss alarm |
| `trigger_alarm` | Manually trigger (testing) |
| `edit_alarm` | Edit alarm properties |
| `list_alarms` | List all alarms |

## Events
- `calendar_alarm_clock.alarm_ringing`
- `calendar_alarm_clock.alarm_snoozed`
- `calendar_alarm_clock.alarm_dismissed`
- `calendar_alarm_clock.alarm_timed_out`
- `calendar_alarm_clock.alarm_created`
- `calendar_alarm_clock.alarm_deleted`
- `calendar_alarm_clock.alarm_edited`
- `calendar_alarm_clock.alarm_enabled`
- `calendar_alarm_clock.alarm_disabled`

## Entities
- `sensor.<entry>_<alarm_id>` - Individual alarm sensor
- `sensor.<entry>_next_alarm` - Next upcoming alarm
- `sensor.<entry>_previous_alarm` - Most recent alarm

## Lovelace Card Views
1. **List View** (default): Shows all alarms for the week
2. **Single Alarm View**: Detailed view when `entity` is configured

## File Structure
```
custom_components/calendar_alarm_clock/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── models.py
├── alarm_manager.py
├── sensor.py
├── services.py
├── services.yaml
├── strings.json
├── translations/en.json
└── www/alarm-clock-card.js

frontend/
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .yarnrc.yml
└── src/
    ├── main.ts
    ├── types.ts
    ├── env.d.ts
    └── AlarmClockCard.vue
```

## Build Instructions
```bash
cd frontend
yarn install
yarn build
```

## CI/CD
- **CI** (`ci.yml`): Runs on push/PR to `mane`/`main`
  - Python linting with Ruff
  - Frontend TypeScript check and build
  - HACS validation
  - Hassfest validation
- **Release** (`release.yml`): Runs on version tags (`v*`)
  - Builds frontend
  - Creates release zip
  - Publishes to GitHub Releases

## Creating a Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Installation
1. Add via HACS: `https://github.com/luckydonald/hoass_calendar-alarm-clock`
2. Or manually copy `custom_components/calendar_alarm_clock` to HA config
3. Add card resource: `/local/alarm-clock-card.js`
4. Configure integration via UI

## Links
- [GitHub Repository](https://github.com/luckydonald/hoass_calendar-alarm-clock)
- [Issue Tracker](https://github.com/luckydonald/hoass_calendar-alarm-clock/issues)

