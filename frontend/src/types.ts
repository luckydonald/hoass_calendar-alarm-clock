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
    target?: { entity_id?: string | string[] }
  ) => Promise<void>;
}

export interface CardConfig {
  type?: string;
  entity?: string;
  title?: string;
}

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

