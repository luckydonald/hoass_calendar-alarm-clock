# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Calendar backed Alarm Clock for Home Assistant** — a HACS custom component that stores alarms as CalDAV calendar events instead of locally. This enables calendar-native persistence, multi-device sync, and integration with existing calendar workflows.

## Commands

### Setup
```bash
make setup          # Full dev environment (Python + frontend)
make setup-py       # Python only: uv sync
make setup-ts       # Frontend only: yarn install
```

### Testing
```bash
make test           # All tests
make test-py        # Backend: uv run pytest tests/
make test-ts        # Frontend: cd frontend && yarn test
make test-coverage  # All tests with HTML coverage reports
```

### Linting & Formatting
```bash
make lint           # All linters
make lint-py        # ruff check + ruff format --check
make lint-ts        # vue-tsc + eslint

make format         # Format all code
make format-py      # ruff check --fix + ruff format
make format-ts      # dprint fmt + eslint --fix
```

### Build & Release
```bash
make build          # Build frontend (Vite)
make commit         # Commit with structured messages via scripts/commit.sh
make release        # Bump version, lint, build, commit, tag, push
```

Single test: `uv run pytest tests/test_models.py -k test_name`

## Architecture

This is a dual-stack project: Python backend (HA integration) + Vue 3 frontend (Lovelace card).

### Backend: `custom_components/calendar_alarm_clock/`

**Key modules and their roles:**

- `__init__.py` — Entry point: registers static www path, sets up `AlarmManager` per config entry, handles auto-discovery
- `alarm_manager.py` — Core engine: polls calendar every 30s, detects ringing alarms, fires HA events, manages snooze/dismiss lifecycle
- `models.py` — `Alarm` dataclass: parses CalDAV events, detects state prefixes (`[SNOOZE {i}]`, `[DISMISSED]`, `[DISABLED]`)
- `sensor.py` — Dynamic sensor entities: one per alarm event plus global next/previous sensors
- `services.py` — 8 HA services: `create_alarm`, `delete_alarm`, `enable_alarm`, `disable_alarm`, `edit_alarm`, `snooze_alarm`, `dismiss_alarm`, `trigger_alarm`
- `config_flow.py` — Two setup modes: auto-discovery (finds all calendars) or manual (user selects one)

**Alarm state machine:** `before → ringing → snoozed → ringing_snooze → dismissed | timed_out`

**CalDAV naming conventions** (state is encoded in the event summary/id):
- Snooze: creates new event with `[SNOOZE {i}] ` prefix, ID = `{original_id}-snooze-{i}`
- Dismiss: adds `[DISMISSED] ` prefix to event summary, sets status to free
- Disabled: adds `[DISABLED] ` prefix

**Events fired:** `calendar_alarm_clock.alarm_ringing`, `.alarm_snoozed`, `.alarm_dismissed`, `.alarm_timed_out`, `.alarm_created`, `.alarm_deleted`, `.alarm_edited`, `.alarm_enabled`, `.alarm_disabled`

### Frontend: `frontend/src/`

Vue 3 + TypeScript custom elements registered as `<calender-alarm-clock-card>` and `<calender-alarm-clock-editor>`.

- `AlarmClockCard.vue` — Main Lovelace card: analog/digital clock with animation modes (ticks/smooth/DB), alarm list, quick alarm, ringing state display
- `AlarmClockCardEditor.vue` — Config editor as Vue component (avoids shadow-DOM focus loss issues)
- `ColorPicker.vue` — Reusable component with text field + HA dropdown (CSS vars + color names) + native color input, all synced

**Frontend conventions:**
- `<script setup lang="ts">` single-file components
- `<style scoped lang="scss">` — prefer scoped SCSS over inline styles
- HTML attributes: one per line, closing `>` on its own line
- Use `<ha-icon>`, `<ha-card>`, `<ha-button>` etc. from HA frontend where possible
- Be mindful of shadow-DOM inside `ha-*` components

### Entity/Device Structure

Per calendar integration instance:
- **Overview device** (`.overview`): `.previous`, `.current`, `.next` sensors + today count sensors (`.today.total`, `.today.upcoming`, `.today.past`)
- **Alarm entry devices** (`.entry.{event_id}`): one per calendar event with a `.ringing` binary sensor

Entity ID suffix pattern: `{integration_name}.{calendar_id}.{rest}`

## Code Style

**Python:**
- Python 3.12+, full type annotations required (mypy strict mode)
- Prefer async/await throughout
- Early-return pattern to reduce nesting — prefer `if … continue/return/break` over large nested blocks
- Line length: 100 chars (ruff)
- Import HA types from `homeassistant.*` where available

**TypeScript:**
- Full TypeScript types — no `any` or type disabling
- Import HA types from Homeassistant where possible

## AI Context Files

The `ai/` folder contains project history and spec:
- `ai/query.md` — Master specification (all previous AI prompts accumulated)
- `ai/progress.md` — Implementation progress tracking (keep updated)
- `ai/overview.md` — Current state overview (keep updated)
- `ai/errors.md` — Troubleshooting notes
- `ai/apis/` — Reference API documentation
