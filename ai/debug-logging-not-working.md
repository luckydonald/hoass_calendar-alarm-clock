# Debug Logging Not Working

## Problem
Adding this to `configuration.yaml` doesn't seem to enable debug logging:
```yaml
logger:
  logs:
    custom_components.calendar_alarm_clock: debug
```

## Solutions

### Solution 1: Full Logger Configuration
Make sure you have the complete logger configuration in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.calendar_alarm_clock: debug
    custom_components.calendar_alarm_clock.config_flow: debug
    custom_components.calendar_alarm_clock.alarm_manager: debug
```

**Then restart Home Assistant** (full restart, not just reload).

### Solution 2: Set Logging via Developer Tools (No Restart Needed)

1. Go to **Developer Tools** → **Services**
2. Choose service: `logger.set_level`
3. Service data:
```yaml
custom_components.calendar_alarm_clock: debug
custom_components.calendar_alarm_clock.config_flow: debug
custom_components.calendar_alarm_clock.alarm_manager: debug
```
4. Click **Call Service**

**Note**: This is temporary and will reset on HA restart.

### Solution 3: Set Default Logging Level Higher

Sometimes components inherit the default level. Try:

```yaml
logger:
  default: debug  # This is verbose but will show everything
  logs:
    homeassistant: info  # Keep HA core at info to reduce noise
    custom_components.calendar_alarm_clock: debug
```

### Solution 4: Check Logger Configuration

Make sure there's no conflicting configuration:

1. Check if logger is defined multiple times in different files
2. Check `configuration.yaml` for includes that might override
3. Verify indentation is correct (YAML is strict about spaces)

### Solution 5: Enable via UI (Home Assistant 2023.4+)

1. Go to **Settings** → **System** → **Logs**
2. Click **Settings** (gear icon)
3. Find or add `custom_components.calendar_alarm_clock`
4. Set to **Debug**

### Solution 6: Check if Logs Are Being Written

Even if not visible in the UI, logs might be written to file:

```bash
# SSH into Home Assistant or open terminal
tail -f /config/home-assistant.log | grep calendar_alarm_clock
```

Or check the log file:
```bash
grep -i "calendar_alarm_clock" /config/home-assistant.log
```

## Verification Steps

After enabling debug logging, you should see these messages on HA startup:

```
2026-01-16 12:00:00 INFO (MainThread) [custom_components.calendar_alarm_clock] Home Assistant started, checking for auto-discovery opportunity...
2026-01-16 12:00:00 DEBUG (MainThread) [custom_components.calendar_alarm_clock] Auto-discovery entry already exists
```

Or when adding a calendar:
```
2026-01-16 12:05:30 INFO (MainThread) [custom_components.calendar_alarm_clock] New calendar entity detected: calendar.personal, triggering discovery
2026-01-16 12:05:30 INFO (custom_components.calendar_alarm_clock) Found 2 calendar(s), will create auto-discovery entry
```

## If Still Not Working

### Check Integration is Loaded
```yaml
# In Developer Tools → Services
# Call: system_log.write
service_data:
  message: "Test message from Calendar Alarm Clock"
  level: debug
  logger: custom_components.calendar_alarm_clock
```

### Force Reload Integration
1. Go to **Settings** → **Devices & Services**
2. Find **Calendar Alarm Clock**
3. Click **•••** → **Reload**
4. Check logs again

### Restart Home Assistant
Sometimes configuration changes only take effect after a full restart:
1. **Settings** → **System** → **Restart**
2. Choose **Restart Home Assistant**
3. Wait for restart to complete
4. Check logs

## Temporary High-Level Logging (For Debugging)

Add this to `configuration.yaml` to see EVERYTHING (very verbose):

```yaml
logger:
  default: debug
  filters:
    # Reduce noise from these
    homeassistant.core:
      - ".*"
    homeassistant.loader:
      - ".*"
```

**Warning**: This will make logs very large very quickly. Only use temporarily.

## Alternative: Add Print Statements (Development Only)

If logging still doesn't work, temporarily add print statements:

```python
# In __init__.py
print("=" * 80)
print(f"CALENDAR ALARM CLOCK: Found {len(calendars)} calendars")
print("=" * 80)
```

These will appear in the Home Assistant logs regardless of log level.

**Remember to remove these before committing!**

## Expected Log Output

With debug logging enabled, you should see:

```
# On HA startup
INFO: Home Assistant started, checking for auto-discovery opportunity...
DEBUG: Auto-discovery entry already exists
  OR
DEBUG: User has manually configured calendar entries, skipping auto-discovery
  OR
INFO: Found X calendar(s), will create auto-discovery entry

# On calendar detection
INFO: New calendar entity detected: calendar.X, triggering discovery

# On config flow
INFO: Integration discovery triggered with data: {...}
INFO: Auto-discovery entry requested, setting unique_id
INFO: System onboarded: True
INFO: Showing auto-discovery confirmation dialog to user
```

## Summary

**Quick Fix** (No restart needed):
```
Developer Tools → Services → logger.set_level
custom_components.calendar_alarm_clock: debug
```

**Permanent Fix** (Requires restart):
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.calendar_alarm_clock: debug
```

Then **Settings → System → Restart**.

