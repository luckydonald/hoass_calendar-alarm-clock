<script setup lang="ts">
import { computed, ref } from 'vue';
import type {
  Alarm,
  AlarmDialogData,
  AlarmState,
  HomeAssistant,
  NextAlarmInfo,
  RepeatPattern,
} from './types';

// Props
const props = defineProps<{
  hass: HomeAssistant | null;
  config: {
    entity?: string;
    title?: string;
  };
}>();

// State
const showDialog = ref(false);
const isEditing = ref(false);
const editingAlarmId = ref<string | null>(null);
const dialogData = ref<AlarmDialogData>({
  name: 'Alarm',
  time: '07:00',
  date: '',
  repeat: 'none',
  enabled: true,
});

// Computed
const cardTitle = computed(() => props.config.title || 'Alarm Clock');

const isSingleAlarmView = computed(() => !!props.config.entity);

const alarms = computed<Alarm[]>(() => {
  if (!props.hass) return [];

  const result: Alarm[] = [];
  const states = props.hass.states;

  for (const entityId in states) {
    const state = states[entityId];
    if (
      entityId.startsWith('sensor.')
      && state.attributes.alarm_id
      && !entityId.includes('_next_alarm')
      && !entityId.includes('_previous_alarm')
    ) {
      result.push({
        entity_id: entityId,
        alarm_id: state.attributes.alarm_id as string,
        name: (state.attributes.name as string) || 'Alarm',
        time: (state.attributes.time as string) || null,
        enabled: state.attributes.enabled !== false,
        repeat: (state.attributes.repeat as string) || 'none',
        snooze_count: (state.attributes.snooze_count as number) || 0,
        timeout: (state.attributes.timeout as number) || null,
        max_snoozes: (state.attributes.max_snoozes as number) || null,
        snooze_duration: (state.attributes.snooze_duration as number) || null,
        next_snooze_time: (state.attributes.next_snooze_time as string) || null,
        state: state.state as AlarmState,
      });
    }
  }

  return result;
});

const sortedAlarms = computed<Alarm[]>(() => {
  return [...alarms.value].sort((a, b) => {
    const timeA = a.time ? new Date(a.time).getTime() : 0;
    const timeB = b.time ? new Date(b.time).getTime() : 0;
    return timeA - timeB;
  });
});

const selectedAlarm = computed<Alarm | null>(() => {
  if (!props.config.entity || !props.hass) return null;

  const state = props.hass.states[props.config.entity];
  if (!state) return null;

  return {
    entity_id: props.config.entity,
    alarm_id: state.attributes.alarm_id as string,
    name: (state.attributes.name as string) || 'Alarm',
    time: (state.attributes.time as string) || null,
    enabled: state.attributes.enabled !== false,
    repeat: (state.attributes.repeat as string) || 'none',
    snooze_count: (state.attributes.snooze_count as number) || 0,
    timeout: (state.attributes.timeout as number) || null,
    max_snoozes: (state.attributes.max_snoozes as number) || null,
    snooze_duration: (state.attributes.snooze_duration as number) || null,
    next_snooze_time: (state.attributes.next_snooze_time as string) || null,
    state: state.state as AlarmState,
  };
});

const nextAlarm = computed<NextAlarmInfo | null>(() => {
  if (!props.hass) return null;

  for (const entityId in props.hass.states) {
    if (entityId.includes('_next_alarm')) {
      const state = props.hass.states[entityId];
      if (state.state && state.state !== 'unknown') {
        return {
          time: (state.attributes.time as string) || null,
          name: (state.attributes.name as string) || 'Alarm',
          state: (state.attributes.state as AlarmState) || 'before',
        };
      }
    }
  }

  return null;
});

const isNextAlarmRinging = computed(() => {
  return (
    nextAlarm.value
    && (nextAlarm.value.state === 'ringing' || nextAlarm.value.state === 'ringing_snooze')
  );
});

const ringingAlarms = computed<Alarm[]>(() => {
  return alarms.value.filter((alarm) => isAlarmRinging(alarm));
});

// Methods
function formatTime(isoTime: string | null): string {
  if (!isoTime) return '--:--';
  try {
    const date = new Date(isoTime);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoTime;
  }
}

function formatRepeat(repeat: string): string {
  const labels: Record<string, string> = {
    none: 'Once',
    daily: 'Daily',
    weekdays: 'Weekdays',
    weekends: 'Weekends',
    weekly: 'Weekly',
  };
  return labels[repeat] || repeat;
}

function getAlarmIcon(alarm: Alarm): string {
  if (isAlarmRinging(alarm)) return 'mdi:alarm-note';
  if (alarm.state === 'snoozed') return 'mdi:alarm-snooze';
  if (!alarm.enabled) return 'mdi:alarm-off';
  return 'mdi:alarm';
}

function getStatusText(alarm: Alarm): string {
  const states: Record<AlarmState, string> = {
    before: 'Scheduled',
    ringing: '🔔 Ringing!',
    ringing_snooze: '🔔 Ringing (Snoozed)!',
    snoozed: 'Snoozed',
    dismissed: 'Dismissed',
    timed_out: 'Timed Out',
  };
  return states[alarm.state] || alarm.state;
}

function isAlarmRinging(alarm: Alarm): boolean {
  return alarm.state === 'ringing' || alarm.state === 'ringing_snooze';
}

async function toggleAlarm(alarm: Alarm): Promise<void> {
  if (!props.hass) return;

  const service = alarm.enabled ? 'disable_alarm' : 'enable_alarm';
  await props.hass.callService('calendar_alarm_clock', service, {
    alarm_id: alarm.alarm_id,
  });
}

async function snoozeAlarm(alarm: Alarm): Promise<void> {
  if (!props.hass) return;

  await props.hass.callService('calendar_alarm_clock', 'snooze_alarm', {
    alarm_id: alarm.alarm_id,
  });
}

async function dismissAlarm(alarm: Alarm): Promise<void> {
  if (!props.hass) return;

  await props.hass.callService('calendar_alarm_clock', 'dismiss_alarm', {
    alarm_id: alarm.alarm_id,
  });
}

async function deleteAlarm(alarm: Alarm): Promise<void> {
  if (!props.hass) return;

  if (confirm(`Delete alarm "${alarm.name}"?`)) {
    await props.hass.callService('calendar_alarm_clock', 'delete_alarm', {
      alarm_id: alarm.alarm_id,
    });
  }
}

function openAddDialog(): void {
  isEditing.value = false;
  editingAlarmId.value = null;
  dialogData.value = {
    name: 'Alarm',
    time: '07:00',
    date: new Date().toISOString().split('T')[0],
    repeat: 'none',
    enabled: true,
  };
  showDialog.value = true;
}

function openEditDialog(alarm: Alarm): void {
  isEditing.value = true;
  editingAlarmId.value = alarm.alarm_id;

  let time = '07:00';
  let date = new Date().toISOString().split('T')[0];

  if (alarm.time) {
    try {
      const d = new Date(alarm.time);
      time = d.toTimeString().slice(0, 5);
      date = d.toISOString().split('T')[0];
    } catch {
      // Use defaults
    }
  }

  dialogData.value = {
    name: alarm.name,
    time,
    date,
    repeat: alarm.repeat as RepeatPattern,
    enabled: alarm.enabled,
  };
  showDialog.value = true;
}

function closeDialog(): void {
  showDialog.value = false;
}

async function saveAlarm(): Promise<void> {
  if (!props.hass) return;

  if (isEditing.value && editingAlarmId.value) {
    await props.hass.callService('calendar_alarm_clock', 'edit_alarm', {
      alarm_id: editingAlarmId.value,
      name: dialogData.value.name,
      time: dialogData.value.time,
      repeat: dialogData.value.repeat,
      enabled: dialogData.value.enabled,
    });
  } else {
    await props.hass.callService('calendar_alarm_clock', 'create_alarm', {
      name: dialogData.value.name,
      time: dialogData.value.time,
      date: dialogData.value.date,
      repeat: dialogData.value.repeat,
      enabled: dialogData.value.enabled,
    });
  }

  closeDialog();
}

function handleSwitchChange(alarm: Alarm, event: Event): void {
  const target = event.target as HTMLInputElement;
  if (target.checked !== alarm.enabled) {
    toggleAlarm(alarm);
  }
}

function handleDialogEnabledChange(event: Event): void {
  const target = event.target as HTMLInputElement;
  dialogData.value.enabled = target.checked;
}

function handleRepeatChange(event: Event): void {
  const target = event.target as HTMLSelectElement;
  dialogData.value.repeat = target.value as RepeatPattern;
}
</script>

<template>
  <ha-card>
    <h1 class="card-header">
      <ha-icon icon="mdi:alarm" class="header-icon" />
      {{ cardTitle }}
    </h1>

    <div class="card-content">
      <!-- Header with next alarm -->
      <div
        v-if="nextAlarm && !isSingleAlarmView"
        class="next-alarm-header"
        :class="{ ringing: isNextAlarmRinging }"
      >
        <div class="next-alarm-icon" :class="{ shake: isNextAlarmRinging }">
          <ha-icon icon="mdi:alarm" />
        </div>
        <div class="next-alarm-info">
          <div class="next-alarm-label">Next Alarm</div>
          <div class="next-alarm-time">{{ formatTime(nextAlarm.time) }}</div>
          <div class="next-alarm-name">{{ nextAlarm.name }}</div>
        </div>
      </div>

      <!-- Single Alarm View -->
      <div v-if="isSingleAlarmView && selectedAlarm" class="single-alarm-view">
        <div
          class="single-alarm-icon"
          :class="{
            shake: isAlarmRinging(selectedAlarm),
            disabled: !selectedAlarm.enabled,
          }"
        >
          <ha-icon :icon="getAlarmIcon(selectedAlarm)" />
        </div>
        <div class="single-alarm-time">{{ formatTime(selectedAlarm.time) }}</div>
        <div class="single-alarm-name">{{ selectedAlarm.name }}</div>
        <div class="single-alarm-status" :class="{ ringing: isAlarmRinging(selectedAlarm) }">
          {{ getStatusText(selectedAlarm) }}
        </div>

        <!-- Ringing actions -->
        <div v-if="isAlarmRinging(selectedAlarm)" class="single-alarm-actions">
          <mwc-button
            raised
            class="snooze-button"
            @click="snoozeAlarm(selectedAlarm)"
          >
            <ha-icon icon="mdi:alarm-snooze" slot="icon" />
            Snooze
          </mwc-button>
          <mwc-button
            raised
            class="dismiss-button"
            @click="dismissAlarm(selectedAlarm)"
          >
            <ha-icon icon="mdi:alarm-off" slot="icon" />
            Dismiss
          </mwc-button>
        </div>

        <!-- Toggle when not ringing -->
        <div v-else class="single-alarm-toggle">
          <ha-switch
            :checked="selectedAlarm.enabled"
            @change="handleSwitchChange(selectedAlarm, $event)"
          />
          <span class="toggle-label">{{ selectedAlarm.enabled ? 'Enabled' : 'Disabled' }}</span>
        </div>

        <!-- Details -->
        <ha-expansion-panel outlined header="Details">
          <div class="details-content">
            <div class="detail-row">
              <span class="detail-label">Repeat</span>
              <span class="detail-value">{{ formatRepeat(selectedAlarm.repeat) }}</span>
            </div>
            <div v-if="selectedAlarm.snooze_count > 0" class="detail-row">
              <span class="detail-label">Snooze Count</span>
              <span class="detail-value">{{ selectedAlarm.snooze_count }}</span>
            </div>
          </div>
        </ha-expansion-panel>

        <!-- Action buttons -->
        <div class="single-alarm-buttons">
          <ha-icon-button @click="openEditDialog(selectedAlarm)">
            <ha-icon icon="mdi:pencil" />
          </ha-icon-button>
          <ha-icon-button class="delete-button" @click="deleteAlarm(selectedAlarm)">
            <ha-icon icon="mdi:delete" />
          </ha-icon-button>
        </div>
      </div>

      <!-- Alarm List View -->
      <div v-else class="alarm-list">
        <!-- Ringing Alarms Banner -->
        <div
          v-for="alarm in ringingAlarms"
          :key="'ringing-' + alarm.alarm_id"
          class="ringing-alarm-banner"
        >
          <div class="ringing-alarm-icon shake">
            <ha-icon icon="mdi:alarm-note" />
          </div>
          <div class="ringing-alarm-info">
            <div class="ringing-alarm-label">ALARM RINGING</div>
            <div class="ringing-alarm-time">{{ formatTime(alarm.time) }}</div>
            <div class="ringing-alarm-name">{{ alarm.name }}</div>
          </div>
          <div class="ringing-alarm-actions">
            <mwc-button
              raised
              dense
              class="snooze-button"
              @click="snoozeAlarm(alarm)"
            >
              <ha-icon icon="mdi:alarm-snooze" slot="icon" />
              Snooze
            </mwc-button>
            <mwc-button
              raised
              dense
              class="dismiss-button"
              @click="dismissAlarm(alarm)"
            >
              <ha-icon icon="mdi:alarm-off" slot="icon" />
              Dismiss
            </mwc-button>
          </div>
        </div>

        <div v-if="alarms.length === 0" class="no-alarms">
          <ha-icon icon="mdi:alarm-plus" />
          <p>No alarms scheduled</p>
        </div>

        <ha-list>
          <ha-list-item
            v-for="alarm in sortedAlarms"
            :key="alarm.alarm_id"
            class="alarm-item"
            :class="{
              ringing: isAlarmRinging(alarm),
              disabled: !alarm.enabled,
            }"
            graphic="icon"
            hasMeta
          >
            <ha-icon
              slot="graphic"
              :icon="getAlarmIcon(alarm)"
              class="alarm-icon"
              :class="{ shake: isAlarmRinging(alarm) }"
            />

            <span class="alarm-primary">
              <span class="alarm-time">{{ formatTime(alarm.time) }}</span>
              <span class="alarm-name">{{ alarm.name }}</span>
            </span>

            <span v-if="alarm.repeat !== 'none'" class="alarm-secondary">
              {{ formatRepeat(alarm.repeat) }}
            </span>

            <div slot="meta" class="alarm-actions">
              <template v-if="isAlarmRinging(alarm)">
                <ha-icon-button @click.stop="snoozeAlarm(alarm)">
                  <ha-icon icon="mdi:alarm-snooze" />
                </ha-icon-button>
                <ha-icon-button @click.stop="dismissAlarm(alarm)">
                  <ha-icon icon="mdi:alarm-off" />
                </ha-icon-button>
              </template>
              <template v-else>
                <ha-switch
                  :checked="alarm.enabled"
                  @change="handleSwitchChange(alarm, $event)"
                  @click.stop
                />
                <ha-icon-button @click.stop="openEditDialog(alarm)">
                  <ha-icon icon="mdi:pencil" />
                </ha-icon-button>
                <ha-icon-button @click.stop="deleteAlarm(alarm)">
                  <ha-icon icon="mdi:delete" />
                </ha-icon-button>
              </template>
            </div>
          </ha-list-item>
        </ha-list>
      </div>

      <!-- Add Alarm FAB -->
      <ha-fab
        v-if="!isSingleAlarmView"
        extended
        label="Add Alarm"
        @click="openAddDialog"
      >
        <ha-icon slot="icon" icon="mdi:plus" />
      </ha-fab>
    </div>

    <!-- Add/Edit Dialog -->
    <ha-dialog
      :open="showDialog"
      heading=""
      @closed="closeDialog"
    >
      <div slot="heading" class="dialog-heading">
        <ha-icon :icon="isEditing ? 'mdi:pencil' : 'mdi:alarm-plus'" />
        <span>{{ isEditing ? 'Edit Alarm' : 'Add Alarm' }}</span>
      </div>

      <div class="dialog-content">
        <ha-textfield
          label="Name"
          :value="dialogData.name"
          @input="dialogData.name = ($event.target as HTMLInputElement).value"
        />

        <div class="form-row">
          <label class="form-label">Time</label>
          <input
            type="time"
            class="ha-time-input"
            :value="dialogData.time"
            @input="dialogData.time = ($event.target as HTMLInputElement).value"
          />
        </div>

        <div class="form-row">
          <label class="form-label">Date</label>
          <input
            type="date"
            class="ha-date-input"
            :value="dialogData.date"
            @input="dialogData.date = ($event.target as HTMLInputElement).value"
          />
        </div>

        <ha-select
          label="Repeat"
          :value="dialogData.repeat"
          @selected="handleRepeatChange"
        >
          <mwc-list-item value="none">Never</mwc-list-item>
          <mwc-list-item value="daily">Daily</mwc-list-item>
          <mwc-list-item value="weekdays">Weekdays</mwc-list-item>
          <mwc-list-item value="weekends">Weekends</mwc-list-item>
          <mwc-list-item value="weekly">Weekly</mwc-list-item>
        </ha-select>

        <ha-formfield label="Enabled">
          <ha-switch
            :checked="dialogData.enabled"
            @change="handleDialogEnabledChange"
          />
        </ha-formfield>
      </div>

      <mwc-button slot="secondaryAction" dialogAction="cancel">
        Cancel
      </mwc-button>
      <mwc-button slot="primaryAction" @click="saveAlarm">
        Save
      </mwc-button>
    </ha-dialog>
  </ha-card>
</template>

<style scoped>
:host {
  --alarm-ringing-color: var(--error-color, #db4437);
  --alarm-snooze-color: var(--warning-color, #ff9800);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
}

.header-icon {
  --mdc-icon-size: 24px;
}

.card-content {
  padding: 0 16px 16px;
}

/* Next Alarm Header */
.next-alarm-header {
  display: flex;
  align-items: center;
  padding: 16px;
  margin: 0 -16px 16px;
  background: var(--primary-color);
  color: var(--text-primary-color, #fff);
}

.next-alarm-header.ringing {
  background: var(--alarm-ringing-color);
  animation: pulse 1s ease-in-out infinite;
}

.next-alarm-icon {
  --mdc-icon-size: 48px;
  margin-right: 16px;
}

.next-alarm-label {
  font-size: 12px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.next-alarm-time {
  font-size: 32px;
  font-weight: 500;
  line-height: 1.2;
}

.next-alarm-name {
  font-size: 14px;
  opacity: 0.9;
}

/* Single Alarm View */
.single-alarm-view {
  text-align: center;
  padding: 24px 0;
}

.single-alarm-icon {
  --mdc-icon-size: 72px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.single-alarm-icon.shake {
  color: var(--alarm-ringing-color);
}

.single-alarm-icon.disabled {
  color: var(--disabled-text-color);
}

.single-alarm-time {
  font-size: 48px;
  font-weight: 400;
  color: var(--primary-text-color);
  font-variant-numeric: tabular-nums;
}

.single-alarm-name {
  font-size: 20px;
  color: var(--secondary-text-color);
  margin-bottom: 4px;
}

.single-alarm-status {
  font-size: 14px;
  color: var(--secondary-text-color);
  margin-bottom: 24px;
}

.single-alarm-status.ringing {
  color: var(--alarm-ringing-color);
  font-weight: 500;
}

.single-alarm-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.snooze-button {
  --mdc-theme-primary: var(--alarm-snooze-color);
}

.dismiss-button {
  --mdc-theme-primary: var(--alarm-ringing-color);
}

.single-alarm-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.toggle-label {
  font-size: 14px;
  color: var(--primary-text-color);
}

.details-content {
  padding: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--divider-color);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: var(--secondary-text-color);
}

.detail-value {
  font-weight: 500;
  color: var(--primary-text-color);
}

.single-alarm-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}

.delete-button {
  --mdc-icon-button-ink-color: var(--alarm-ringing-color);
}

/* Alarm List */
.alarm-list {
  margin: 0 -16px;
}

/* Ringing Alarm Banner */
.ringing-alarm-banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  margin: 0 0 8px 0;
  background: var(--error-color, #db4437);
  color: white;
  text-align: center;
  animation: pulse 1s ease-in-out infinite;
}

.ringing-alarm-icon {
  --mdc-icon-size: 56px;
  margin-bottom: 8px;
}

.ringing-alarm-info {
  margin-bottom: 16px;
}

.ringing-alarm-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.ringing-alarm-time {
  font-size: 40px;
  font-weight: 500;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.ringing-alarm-name {
  font-size: 16px;
  opacity: 0.9;
}

.ringing-alarm-actions {
  display: flex;
  gap: 12px;
}

.ringing-alarm-actions .snooze-button {
  --mdc-theme-primary: var(--warning-color, #ff9800);
  --mdc-theme-on-primary: white;
}

.ringing-alarm-actions .dismiss-button {
  --mdc-theme-primary: rgba(255, 255, 255, 0.2);
  --mdc-theme-on-primary: white;
}

.no-alarms {
  text-align: center;
  padding: 48px 16px;
  color: var(--secondary-text-color);
}

.no-alarms ha-icon {
  --mdc-icon-size: 64px;
  opacity: 0.5;
  margin-bottom: 16px;
}

.no-alarms p {
  margin: 0;
  font-size: 16px;
}

ha-list {
  --mdc-list-vertical-padding: 0;
}

.alarm-item {
  --mdc-list-item-graphic-margin: 16px;
}

.alarm-item.ringing {
  background: rgba(var(--rgb-error-color, 219, 68, 55), 0.1);
}

.alarm-item.disabled {
  opacity: 0.6;
}

.alarm-icon {
  --mdc-icon-size: 32px;
  color: var(--primary-color);
}

.alarm-item.ringing .alarm-icon {
  color: var(--alarm-ringing-color);
}

.alarm-primary {
  display: flex;
  flex-direction: column;
}

.alarm-time {
  font-size: 20px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.alarm-name {
  font-size: 14px;
  color: var(--secondary-text-color);
}

.alarm-secondary {
  font-size: 12px;
  color: var(--secondary-text-color);
}

.alarm-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* FAB */
ha-fab {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 1;
}

/* Dialog */
.dialog-heading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-heading ha-icon {
  --mdc-icon-size: 24px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

ha-textfield,
ha-select {
  width: 100%;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--secondary-text-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ha-time-input,
.ha-date-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--divider-color);
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  background: var(--card-background-color);
  color: var(--primary-text-color);
  box-sizing: border-box;
}

.ha-time-input:focus,
.ha-date-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

ha-formfield {
  display: flex;
  align-items: center;
  --mdc-typography-body2-font-size: 14px;
}

/* Animations */
.shake {
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0) rotate(0deg);
  }
  10% {
    transform: translateX(-2px) rotate(-5deg);
  }
  20% {
    transform: translateX(2px) rotate(5deg);
  }
  30% {
    transform: translateX(-2px) rotate(-5deg);
  }
  40% {
    transform: translateX(2px) rotate(5deg);
  }
  50% {
    transform: translateX(-1px) rotate(-2deg);
  }
  60% {
    transform: translateX(1px) rotate(2deg);
  }
  70% {
    transform: translateX(-1px) rotate(-2deg);
  }
  80% {
    transform: translateX(1px) rotate(2deg);
  }
  90% {
    transform: translateX(0) rotate(0deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
