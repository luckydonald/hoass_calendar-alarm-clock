// Home Assistant types
export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
  context: {
    id: string;
    parent_id: string | null;
    user_id: string | null;
  };
}

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  services: Record<string, Record<string, unknown>>;
  user: {
    id: string;
    name: string;
    is_admin: boolean;
  };
  language: string;
  callService: (
    domain: string,
    service: string,
    data?: Record<string, unknown>,
    target?: { entity_id?: string | string[]; },
  ) => Promise<void>;
}

export interface CardConfig {
  type?: string;
  entity?: string;
  title?: string;
  // Add your custom config options here

  // Clock display options
  clock_display?: 'analog' | 'analog-24h' | '24h' | '12h' | 'none';
  // Clock color and seconds options
  clock_bg_color?: string;
  clock_hour_color?: string;
  clock_minute_color?: string;
  clock_second_color?: string;
  clock_middle_color?: string;
  clock_show_seconds?: boolean;
  // Animation mode for the clock: 'ticks' (discrete), 'smooth' (continuous), or 'db' (special DB behavior)
  clock_animation_mode?: 'ticks' | 'smooth' | 'db';
  // Alarm list options
  alarm_list_mode?: 'days' | 'count';
  alarm_list_days?: number;
  alarm_list_count?: number;
  // Section visibility
  show_clock?: boolean;
  show_quick_alarm?: boolean;
  show_alarm_list?: boolean;
  show_add_section?: 'on' | 'off' | 'auto';
  // Section collapsed state
  collapse_clock?: boolean;
  collapse_quick_alarm?: boolean;
  collapse_alarm_list?: boolean;
  collapse_add_section?: boolean;
}

export type AnalogClockAnimationMode = CardConfig['clock_animation_mode'];

// Alarm types
export interface AlarmAttributes {
  alarm_id: string;
  name: string;
  time: string | null;
  enabled: boolean;
  repeat: string;
  next_snooze_time: string | null;
  snooze_count: number;
  timeout: number | null;
  max_snoozes: number | null;
  snooze_duration: number | null;
}

export interface Alarm extends AlarmAttributes {
  entity_id: string;
  state: AlarmState;
}

export type AlarmState =
  | 'before'
  | 'ringing'
  | 'ringing_snooze'
  | 'snoozed'
  | 'dismissed'
  | 'timed_out';

export type RepeatPattern =
  | 'none'
  | 'daily'
  | 'weekdays'
  | 'weekends'
  | 'weekly';

export type ClockDisplay = 'analog' | '24h' | '12h' | 'none';

export type AlarmListMode = 'days' | 'count';

export type AddSectionMode = 'on' | 'off' | 'auto';

export interface AlarmDialogData {
  name: string;
  time: string;
  date: string;
  repeat: RepeatPattern;
  enabled: boolean;
}

export interface NextAlarmInfo {
  time: string | null;
  name: string;
  state: AlarmState;
}

export interface QuickAlarmOption {
  label: string;
  minutes: number;
  icon: string;
}
