# Auto-Discovery Configuration Feature

## Overview
Added a configuration option during initial integration setup that allows users to control whether calendars should be automatically discovered and offered for alarm clock setup.

## Implementation Details

### Changes Made

#### 1. Constants (`const.py`)
- Added `CONF_AUTO_DISCOVER_CALENDARS` constant for storing the user's preference

#### 2. Config Flow (`config_flow.py`)
- **Modified `async_step_user`**: Now the initial step that asks about auto-discovery preference
  - Shows count of available calendars
  - Presents choice between auto-discovery and manual setup
  - Routes to appropriate next step based on user choice

- **Added `async_step_auto_discover`**:
  - Creates a special "auto_discovery" config entry
  - Triggers calendar discovery immediately
  - Uses unique_id "auto_discovery" to prevent duplicates

- **Added `async_step_manual`**:
  - Renamed from old `async_step_user`
  - Shows calendar entity selector
  - User manually chooses which calendar to configure

- **Added `_trigger_discovery` helper**:
  - Waits briefly for config entry to be set up
  - Triggers the discovery process

- **Modified `async_discover_calendars`**:
  - Now checks if auto-discovery is enabled before creating discovery flows
  - Only discovers calendars if at least one config entry has `CONF_AUTO_DISCOVER_CALENDARS: True`

#### 3. Translations (`strings.json` and `translations/en.json`)
- Updated `user` step: Now explains auto-discovery vs manual setup
  - Shows calendar count
  - Explains pros/cons of each option

- Added `manual` step: For calendar selection in manual mode
  - Retains original calendar selection UI

### User Experience Flow

#### Option 1: Auto-Discovery Enabled
1. User adds integration
2. Sees initial screen: "Found X calendar(s)" with checkbox for auto-discovery
3. Enables auto-discovery checkbox
4. Integration creates "Calendar Alarm Clock (Auto-Discovery)" entry
5. Discovery flows automatically appear for all unconfigured calendars
6. User can accept/reject each calendar individually

#### Option 2: Manual Setup
1. User adds integration
2. Sees initial screen, leaves auto-discovery disabled
3. Shown calendar selector
4. Manually picks a calendar
5. Integration creates "Alarm Clock (calendar_name)" entry
6. No automatic discovery for other calendars

### Benefits
- **Less spam**: Users with many calendars can opt out of auto-discovery
- **Flexibility**: Users can choose between convenience (auto) and control (manual)
- **Transparency**: Clear explanation of what each option does
- **Progressive disclosure**: Only shows complexity when needed

### Technical Notes
- Auto-discovery entry uses unique_id "auto_discovery" to prevent duplicates
- **Auto-discovery entries are lightweight**: They don't create AlarmManager or sensors, just enable discovery
- **Regular calendar entries**: Create AlarmManager, sensors, and handle alarm logic
- `async_setup_entry` checks `CONF_AUTO_DISCOVER_CALENDARS` to determine entry type
- `async_unload_entry` handles both entry types appropriately
- Manual calendar entries use the calendar entity_id as unique_id (as before)
- Discovery only triggers if auto-discovery is enabled
- Backward compatible: existing installations continue working (discovery on by default)

## Bug Fixes
- **Fixed KeyError on auto-discovery entry setup**: Auto-discovery entries don't have `calendar_entity` in their data, so `async_setup_entry` now checks the entry type first and handles each appropriately

## Testing Checklist
- [ ] Initial setup with auto-discovery enabled works
- [ ] Initial setup with auto-discovery disabled works
- [ ] Auto-discovery correctly discovers new calendars when enabled
- [ ] Auto-discovery doesn't discover when disabled
- [ ] Multiple manual calendar setups work independently
- [ ] Cannot create duplicate auto-discovery entry
- [ ] Cannot create duplicate manual calendar entries
- [ ] Translations display correctly
- [ ] Calendar count shows correctly in initial screen

## Future Enhancements
- Add option to toggle auto-discovery in options flow (for existing installations)
- Allow filtering which calendars to auto-discover (e.g., by name pattern)
- Add option to auto-dismiss discovery notifications after X days

