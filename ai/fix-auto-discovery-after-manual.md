# Bug Fix: Auto-Discovery Appearing After Manual Setup

## Problem Report
> "Alarm Clock for Auto-Discovery Calendar backed Alarm Clock" appears _after_ I added a calendar manually, so maybe it's logic when to appear is wrong?

## The Issue

When a user manually added a calendar through the integration setup, they would see the auto-discovery confirmation dialog appear afterward. This was confusing and annoying because:

1. User explicitly chose manual setup by adding the integration manually
2. User selected a specific calendar to configure
3. System should have respected this choice
4. Instead, system offered auto-discovery, which the user already declined by choosing manual

## Root Cause

The `_async_auto_create_discovery_entry()` function had incomplete logic:

```python
# OLD LOGIC (BROKEN)
for entry in hass.config_entries.async_entries(DOMAIN):
    if entry.data.get(CONF_AUTO_DISCOVER_CALENDARS, False):
        return  # Auto-discovery entry exists, don't create

# If we get here, no auto-discovery entry exists
# → Create one!
```

**Problem**: This only checked if an auto-discovery entry existed. It didn't check if the user had already manually configured calendars.

**Scenario**:
1. User manually adds calendar → Creates entry with `{CONF_CALENDAR_ENTITY: "calendar.foo"}`
2. System checks for auto-discovery entry → Not found
3. System thinks: "No auto-discovery! Let me offer it!"
4. User gets unwanted notification

## The Fix

Enhanced the logic to detect and respect manual setup:

```python
# NEW LOGIC (FIXED)
has_auto_discovery = False
has_manual_entries = False

for entry in hass.config_entries.async_entries(DOMAIN):
    if entry.data.get(CONF_AUTO_DISCOVER_CALENDARS, False):
        has_auto_discovery = True
    else:
        # This entry has a calendar_entity, so it's manually configured
        has_manual_entries = True

if has_auto_discovery:
    return  # Already using auto-discovery

if has_manual_entries:
    return  # User chose manual setup, respect that choice!

# Only create auto-discovery if no entries exist yet
```

## How Entries Are Distinguished

**Auto-Discovery Entry**:
```python
{
    "auto_discover_calendars": True
}
```

**Manual Calendar Entry**:
```python
{
    "calendar_entity": "calendar.my_calendar"
}
```

If an entry has `calendar_entity`, it's a manual entry.
If an entry has `auto_discover_calendars`, it's the auto-discovery entry.

## New Behavior

### Scenario 1: Fresh Install, No Calendars
- No calendars exist → No entries created
- User adds calendar integration → Auto-discovery notification appears
- User can accept or decline

### Scenario 2: Fresh Install, Manual Setup
- User manually adds integration → Chooses specific calendar
- Entry created with `calendar_entity`
- Auto-discovery check sees manual entry → Skips creation
- **No auto-discovery notification appears** ✓

### Scenario 3: Auto-Discovery Enabled
- User accepts auto-discovery → Entry created with `auto_discover_calendars`
- Auto-discovery check sees auto-discovery entry → Skips creation
- Individual calendar discoveries appear as normal ✓

### Scenario 4: Mixed Setup
- User has manual entries already
- Auto-discovery is never offered (respects manual choice)
- User can still manually add more calendars ✓

## Testing

To verify the fix:

1. **Clean install**: Remove all Calendar Alarm Clock entries
2. **Manual setup**: Go to Integrations → Add → Calendar Alarm Clock → Select calendar
3. **Restart HA**: Restart Home Assistant
4. **Check notifications**: No auto-discovery notification should appear
5. **Check logs**: Should see "User has manually configured calendar entries, skipping auto-discovery"

## Log Messages

**Before Fix** (wrong behavior):
```
INFO: Found 1 calendar(s), will create auto-discovery entry
INFO: Creating auto-discovery flow...
```
(Even though user manually set up a calendar)

**After Fix** (correct behavior):
```
DEBUG: User has manually configured calendar entries, skipping auto-discovery
```
(Respects user's manual setup choice)

## Impact

- ✅ Respects user's explicit choice to use manual setup
- ✅ No unwanted notifications after manual configuration
- ✅ Auto-discovery still works for fresh installs
- ✅ Users can still choose auto-discovery if they want
- ✅ Cleaner, less confusing user experience

## Related Files

- `custom_components/calendar_alarm_clock/__init__.py` - `_async_auto_create_discovery_entry()`
- `ai/auto-discovery-implementation-summary.md` - Full implementation details
- `ai/progress.md` - Change log

## Date
Fixed: January 16, 2026

