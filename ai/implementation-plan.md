# Calendar Alarm Clock - Enhanced UI Implementation Plan

## Overview
Enhance the Lovelace card with modern phone-style alarm UI including:
- Big analog/digital clock display
- Ringing alarm banner with action buttons
- Modern alarm list with SVG clocks showing time + day/night
- Quick alarm feature (30min, 1h, 6h, custom)
- Toggleable sections
- Configurable alarm list (by days or count)

## Features Implemented ✅

### 1. Ringing Alarm Display ✅
- [x] Prominent red banner when alarm is ringing
- [x] Large time display
- [x] Snooze and Dismiss action buttons
- [x] Shake animation for icon

### 2. Big Clock Section (Current Time) ✅
- [x] Analog clock SVG with hour/minute/second hands
- [x] 24h digital display option
- [x] 12h digital display option
- [x] Day/night background indicator
- [x] Active alarm indicator (red = within 12h, yellow = future)
- [x] Add alarm button in header

### 3. Quick Alarm Section ✅
- [x] Preset buttons: 30 min, 1h, 6h
- [x] Custom time input
- [x] Fires event for automation triggers
- [x] Collapsible section

### 4. Enhanced Alarm List ✅
- [x] SVG clock icon showing actual alarm time
- [x] Day/night indicator on clock
- [x] Show day of week for alarms
- [x] Configurable: show X days or Y alarms count
- [x] Default: next 7 days
- [x] Collapsible section

### 5. Add Alarm Section ✅
- [x] Show modes: on, off, auto
- [x] Auto mode: shows when "Add" is clicked
- [x] Collapsible section

### 6. Section Toggle System ✅
- [x] Each section can be collapsed/expanded
- [x] Uses ha-expansion-panel for native HA look
- [x] Smooth animations

## Card Configuration Options
```yaml
type: custom:alarm-clock-card
title: Calendar Alarm Clock
clock_display: analog  # analog, 24h, 12h, none
alarm_list_mode: days  # days or count
alarm_list_days: 7     # show alarms for next X days
alarm_list_count: 10   # or show X alarms
show_clock: true
show_quick_alarm: true
show_alarm_list: true
show_add_section: auto  # on, off, auto
collapse_clock: false
collapse_quick_alarm: false
collapse_alarm_list: false
collapse_add_section: true
```

## Files Changed
1. `frontend/src/types.ts` - Added new config types ✅
2. `frontend/src/AlarmClockCard.vue` - Main component completely rewritten ✅
3. `frontend/src/main.ts` - Updated card editor with all new options ✅

