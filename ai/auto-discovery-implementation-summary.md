# Auto-Discovery Entry Implementation Summary

## What Changed

The auto-discovery feature has been enhanced so that the auto-discovery config entry itself is **automatically created** when Home Assistant detects calendars. This means users no longer need to manually add the integration - it just appears automatically.

## How It Works

### Automatic Creation
When Home Assistant starts up or when a new calendar entity is added:

1. The integration checks if any calendars exist
2. If calendars exist and no auto-discovery entry is configured:
   - During onboarding: Auto-discovery entry is created automatically without user interaction
   - After onboarding: A discovery notification appears asking the user to confirm

3. Once the auto-discovery entry exists, it enables automatic discovery of individual calendars
4. Users see discovery notifications for each calendar, which they can accept or reject

### Code Flow

```
HA Startup or New Calendar Added
    ↓
async_setup() in __init__.py
    ↓
_async_auto_create_discovery_entry()
    ↓
Check: Auto-discovery entry exists? → Yes: Exit
    ↓ No
Check: Calendars available? → No: Exit
    ↓ Yes
Check: During onboarding?
    ↓ Yes                      ↓ No
Create entry directly    Show confirmation dialog
    ↓                              ↓
Auto-discovery enabled ← User confirms
    ↓
async_discover_calendars()
    ↓
For each unconfigured calendar:
    Show discovery notification
```

## Implementation Details

### Files Modified

1. **`__init__.py`**:
   - Added `_async_auto_create_discovery_entry()` function
   - Modified `async_setup()` to call it on startup and new calendar detection
   - Modified `async_setup_entry()` to handle auto-discovery entries (no calendar_entity)
   - Modified `async_unload_entry()` to handle auto-discovery entries

2. **`config_flow.py`**:
   - Modified `async_step_integration_discovery()` to handle auto-discovery entry creation
   - Added `async_step_auto_discovery_confirm()` for post-onboarding confirmation
   - User step still available for manual integration addition

3. **`strings.json` and `translations/en.json`**:
   - Added `auto_discovery_confirm` step translations

4. **`const.py`**:
   - Added `CONF_AUTO_DISCOVER_CALENDARS` constant

## User Experience

### Scenario 1: New User During Onboarding
1. User sets up a calendar integration (e.g., CalDAV)
2. Auto-discovery entry is created automatically in background
3. User sees discovery notifications for each calendar
4. User accepts/rejects each calendar
5. Done - no manual integration setup needed!

### Scenario 2: Existing User After Onboarding
1. User sets up a calendar integration
2. User sees notification: "Enable Calendar Alarm Clock Auto-Discovery"
3. User reads explanation and confirms
4. Auto-discovery entry is created
5. User sees discovery notifications for each calendar
6. User accepts/rejects each calendar

### Scenario 3: User Wants Manual Control
1. User goes to Settings → Integrations
2. Clicks "Add Integration"
3. Searches for "Calendar Alarm Clock"
4. Chooses manual setup (unchecks auto-discovery)
5. Selects specific calendar from dropdown
6. Only that calendar is configured

## Key Features

- **Zero-configuration**: Just works automatically
- **Smart**: Only activates when calendars are available
- **Respectful**: Shows confirmation dialog after onboarding
- **Flexible**: Manual setup still available for power users
- **Lightweight**: Auto-discovery entry has minimal overhead

## Technical Notes

### Auto-Discovery Entry
- **unique_id**: `"auto_discovery"`
- **data**: `{CONF_AUTO_DISCOVER_CALENDARS: True}`
- **Purpose**: Enable discovery mechanism
- **Setup**: No AlarmManager, no sensors, just a marker
- **Storage**: `hass.data[DOMAIN][entry_id] = {"auto_discovery": True}`

### Regular Calendar Entry
- **unique_id**: `calendar_entity` (e.g., `"calendar.my_calendar"`)
- **data**: `{CONF_CALENDAR_ENTITY: "calendar.my_calendar"}`
- **Purpose**: Manage alarms for a specific calendar
- **Setup**: Creates AlarmManager, sensors, periodic updates
- **Storage**: `hass.data[DOMAIN][entry_id] = {"manager": manager, "calendar_entity": entity_id}`

## Benefits

1. **Improved UX**: No manual setup required for most users
2. **Discoverability**: Integration appears automatically when relevant
3. **Flexibility**: Power users can still use manual setup
4. **Scalability**: Works whether you have 1 or 100 calendars
5. **Smart Defaults**: Auto-discovery during onboarding, confirmation after

## Future Enhancements

- Add option to toggle auto-discovery in integration options
- Allow filtering which calendars to auto-discover (by name pattern)
- Add "Don't ask again" option in confirmation dialog
- Provide way to disable auto-discovery globally via config

