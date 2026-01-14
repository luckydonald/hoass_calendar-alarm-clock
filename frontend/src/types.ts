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

