# Debugging Auto-Discovery Not Appearing

## Issue
The auto-discovery confirmation dialog "Calendar Alarm Clock (Auto-Discovery)" is not appearing, but calendar discoveries were working before the change.

## Expected Behavior
When Home Assistant starts and calendars are present:
1. `_async_auto_create_discovery_entry()` should run
2. Check if calendars exist
3. Create discovery flow for auto-discovery entry
4. Show confirmation dialog (after onboarding) or auto-create (during onboarding)
5. Once confirmed, individual calendar discoveries should appear

## Debug Steps

### 1. Check Home Assistant Logs
Look for these log messages in order:

```
INFO: Found X calendar(s), will create auto-discovery entry
INFO: Creating auto-discovery flow...
INFO: Integration discovery triggered with data: {'auto_discover_calendars': True}
INFO: Auto-discovery entry requested, setting unique_id
INFO: System onboarded: True/False
```

**If you see:**
- `"Auto-discovery entry already exists"` - Entry already configured, remove it first
- `"No calendars found"` - No calendar integrations set up
- `"Auto-discovery flow already in progress"` - Flow is pending, check notifications
- Nothing - Function not being called

### 2. Check for Existing Configuration
```bash
# In Home Assistant UI:
Settings → Devices & Services → Integrations
```

Look for:
- "Calendar Alarm Clock (Auto-Discovery)" - If exists, auto-discovery is already set up
- Individual calendar entries - If exist but no auto-discovery entry

### 3. Check for Pending Flows
```bash
# In Home Assistant UI:
Settings → Devices & Services → Integrations → (Bell icon for notifications)
```

Look for:
- "Enable Calendar Alarm Clock Auto-Discovery" notification
- Individual calendar discovery notifications

### 4. Force Re-trigger Discovery

#### Option A: Reload Integration (if already installed)
1. Remove the "Calendar Alarm Clock (Auto-Discovery)" entry
2. Restart Home Assistant
3. Check logs for discovery messages

#### Option B: Add New Calendar
1. Add a new calendar integration
2. This should trigger `async_state_changed` event
3. Check logs for discovery messages

#### Option C: Manual Trigger (Developer Tools)
```yaml
# Not directly possible, but you can:
# 1. Enable debug logging
# 2. Restart Home Assistant
# 3. Watch logs
```

### 5. Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.calendar_alarm_clock: debug
    custom_components.calendar_alarm_clock.config_flow: debug
```

Then restart Home Assistant and check logs.

## Common Issues

### Issue 1: Already Configured
**Symptom**: Log shows "Auto-discovery entry already exists"
**Solution**: Remove existing "Calendar Alarm Clock (Auto-Discovery)" entry and restart

### Issue 2: No Calendars
**Symptom**: Log shows "No calendars found"
**Solution**: Set up a calendar integration (CalDAV, Google Calendar, etc.) first

### Issue 3: Pending Flow Not Visible
**Symptom**: Flow created but no notification
**Solution**:
- Check notification bell icon in Integrations page
- Flow might have been dismissed accidentally
- Check browser console for errors

### Issue 4: Onboarding Check
**Symptom**: Nothing happens after discovery flow creation
**Solution**:
- If system is not onboarded: Entry should auto-create (no notification)
- If system is onboarded: Should show confirmation dialog
- Check log for "System onboarded: True/False"

### Issue 5: Flow Aborted
**Symptom**: Discovery triggered but immediately aborted
**Solution**: Check for `_abort_if_unique_id_configured()` messages

## Testing Checklist

- [ ] Home Assistant is fully started
- [ ] At least one calendar integration is set up
- [ ] No existing "Calendar Alarm Clock (Auto-Discovery)" entry
- [ ] No pending flows for "auto_discovery" unique_id
- [ ] Debug logging is enabled
- [ ] Checked notification bell icon
- [ ] Checked Home Assistant logs for INFO/DEBUG messages

## Log Message Reference

| Message | Meaning |
|---------|---------|
| `Found X calendar(s), will create auto-discovery entry` | Calendars detected, will trigger discovery |
| `Creating auto-discovery flow...` | Discovery flow being created |
| `Auto-discovery entry already exists` | Entry already configured |
| `No calendars found` | No calendar integrations |
| `Auto-discovery flow already in progress` | Flow pending |
| `Integration discovery triggered` | Flow handler called |
| `System onboarded: True` | Will show confirmation dialog |
| `System onboarded: False` | Will auto-create entry |
| `Creating auto-discovery entry automatically` | Auto-creating during onboarding |
| `Showing auto-discovery confirmation dialog` | Showing dialog after onboarding |

## Solution if Still Not Working

If auto-discovery still doesn't appear after checking all above:

1. **Manually add integration**:
   - Settings → Integrations → Add Integration
   - Search "Calendar Alarm Clock"
   - Follow setup wizard

2. **Check for errors**:
   - Look for Python exceptions in logs
   - Check browser console for JavaScript errors

3. **Verify integration files**:
   - Ensure all files are in `custom_components/calendar_alarm_clock/`
   - Restart Home Assistant after file changes

4. **Report issue with logs**:
   - Enable debug logging
   - Restart Home Assistant
   - Save full log output
   - Report with specific log messages

