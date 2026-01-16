<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Alarm, AlarmDialogData, AlarmState, HomeAssistant, NextAlarmInfo, RepeatPattern } from './types';

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
</script>

<template>
  <ha-card :header="cardTitle">
    <div class="card-content">
      <!-- Header with next alarm -->
      <div v-if="nextAlarm && !isSingleAlarmView" class="next-alarm-header" :class="{ ringing: isNextAlarmRinging }">
        <div class="next-alarm-icon" :class="{ ringing: isNextAlarmRinging }">
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
          :class="{ ringing: isAlarmRinging(selectedAlarm), disabled: !selectedAlarm.enabled }"
        >
          <ha-icon :icon="getAlarmIcon(selectedAlarm)" />
        </div>
        <div class="single-alarm-time">{{ formatTime(selectedAlarm.time) }}</div>
        <div class="single-alarm-name">{{ selectedAlarm.name }}</div>
        <div class="single-alarm-status">{{ getStatusText(selectedAlarm) }}</div>

        <div v-if="isAlarmRinging(selectedAlarm)" class="single-alarm-actions">
          <button class="btn btn-snooze" @click="snoozeAlarm(selectedAlarm)">
            <ha-icon icon="mdi:alarm-snooze" />
            Snooze
          </button>
          <button class="btn btn-dismiss" @click="dismissAlarm(selectedAlarm)">
            <ha-icon icon="mdi:alarm-off" />
            Dismiss
          </button>
        </div>

        <div v-else class="single-alarm-toggle">
          <label class="toggle-label">
            <input type="checkbox" :checked="selectedAlarm.enabled" @change="toggleAlarm(selectedAlarm)" />
            <span class="toggle-slider"></span>
            {{ selectedAlarm.enabled ? 'Enabled' : 'Disabled' }}
          </label>
        </div>

        <div class="single-alarm-details">
          <div class="detail-row">
            <span class="detail-label">Repeat:</span>
            <span class="detail-value">{{ formatRepeat(selectedAlarm.repeat) }}</span>
          </div>
          <div v-if="selectedAlarm.snooze_count > 0" class="detail-row">
            <span class="detail-label">Snooze Count:</span>
            <span class="detail-value">{{ selectedAlarm.snooze_count }}</span>
          </div>
        </div>

        <div class="single-alarm-buttons">
          <button class="btn btn-edit" @click="openEditDialog(selectedAlarm)">
            <ha-icon icon="mdi:pencil" />
            Edit
          </button>
          <button class="btn btn-delete" @click="deleteAlarm(selectedAlarm)">
            <ha-icon icon="mdi:delete" />
            Delete
          </button>
        </div>
      </div>

      <!-- Alarm List View -->
      <div v-else class="alarm-list">
        <div v-if="alarms.length === 0" class="no-alarms">
          <ha-icon icon="mdi:alarm-plus" />
          <p>No alarms scheduled</p>
        </div>

        <div
          v-for="alarm in sortedAlarms"
          :key="alarm.alarm_id"
          class="alarm-item"
          :class="{ ringing: isAlarmRinging(alarm), disabled: !alarm.enabled }"
        >
          <div class="alarm-icon" :class="{ shake: isAlarmRinging(alarm) }">
            <ha-icon :icon="getAlarmIcon(alarm)" />
          </div>

          <div class="alarm-info">
            <div class="alarm-time">{{ formatTime(alarm.time) }}</div>
            <div class="alarm-name">{{ alarm.name }}</div>
            <div v-if="alarm.repeat !== 'none'" class="alarm-repeat">
              {{ formatRepeat(alarm.repeat) }}
            </div>
          </div>

          <div class="alarm-actions">
            <template v-if="isAlarmRinging(alarm)">
              <button class="btn-icon" title="Snooze" @click="snoozeAlarm(alarm)">
                <ha-icon icon="mdi:alarm-snooze" />
              </button>
              <button class="btn-icon" title="Dismiss" @click="dismissAlarm(alarm)">
                <ha-icon icon="mdi:alarm-off" />
              </button>
            </template>
            <template v-else>
              <label class="toggle">
                <input type="checkbox" :checked="alarm.enabled" @change="toggleAlarm(alarm)" />
                <span class="toggle-slider"></span>
              </label>
              <button class="btn-icon" title="Edit" @click="openEditDialog(alarm)">
                <ha-icon icon="mdi:pencil" />
              </button>
              <button class="btn-icon" title="Delete" @click="deleteAlarm(alarm)">
                <ha-icon icon="mdi:delete" />
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Add Alarm Button -->
      <div v-if="!isSingleAlarmView" class="add-alarm">
        <button class="btn btn-add" @click="openAddDialog">
          <ha-icon icon="mdi:plus" />
          Add Alarm
        </button>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEditing ? 'Edit Alarm' : 'Add Alarm' }}</h3>
          <button class="btn-icon" @click="closeDialog">
            <ha-icon icon="mdi:close" />
          </button>
        </div>
        <div class="dialog-content">
          <div class="form-row">
            <label>Name</label>
            <input v-model="dialogData.name" type="text" placeholder="Alarm" />
          </div>
          <div class="form-row">
            <label>Time</label>
            <input v-model="dialogData.time" type="time" />
          </div>
          <div class="form-row">
            <label>Date</label>
            <input v-model="dialogData.date" type="date" />
          </div>
          <div class="form-row">
            <label>Repeat</label>
            <select v-model="dialogData.repeat">
              <option value="none">Never</option>
              <option value="daily">Daily</option>
              <option value="weekdays">Weekdays</option>
              <option value="weekends">Weekends</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
          <div class="form-row">
            <label class="checkbox-label">
              <input v-model="dialogData.enabled" type="checkbox" />
              Enabled
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-cancel" @click="closeDialog">Cancel</button>
          <button class="btn btn-save" @click="saveAlarm">Save</button>
        </div>
      </div>
    </div>
  </ha-card>
</template>

<style scoped>
.card-content {
  padding: 16px;
}

/* Next Alarm Header */
.next-alarm-header {
  display: flex;
  align-items: center;
  padding: 16px;
  margin: -16px -16px 16px -16px;
  background: var(--primary-color);
  color: var(--text-primary-color, #fff);
  border-radius: 0;
}

.next-alarm-icon {
  font-size: 48px;
  margin-right: 16px;
}

.next-alarm-icon.ringing {
  animation: shake 0.5s ease-in-out infinite;
}

.next-alarm-label {
  font-size: 12px;
  opacity: 0.8;
  text-transform: uppercase;
}

.next-alarm-time {
  font-size: 32px;
  font-weight: bold;
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
  font-size: 64px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.single-alarm-icon.ringing {
  color: var(--error-color, #f44336);
  animation: shake 0.5s ease-in-out infinite;
}

.single-alarm-icon.disabled {
  color: var(--disabled-text-color, #9e9e9e);
}

.single-alarm-time {
  font-size: 48px;
  font-weight: bold;
  color: var(--primary-text-color);
}

.single-alarm-name {
  font-size: 20px;
  color: var(--secondary-text-color);
  margin-bottom: 8px;
}

.single-alarm-status {
  font-size: 14px;
  color: var(--secondary-text-color);
  margin-bottom: 24px;
}

.single-alarm-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.single-alarm-toggle {
  margin-bottom: 24px;
}

.single-alarm-details {
  text-align: left;
  padding: 16px;
  background: var(--secondary-background-color, #f5f5f5);
  border-radius: 8px;
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--divider-color, #e0e0e0);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: var(--secondary-text-color);
}

.detail-value {
  font-weight: 500;
}

.single-alarm-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* Alarm List */
.alarm-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.no-alarms {
  text-align: center;
  padding: 32px;
  color: var(--secondary-text-color);
}

.no-alarms ha-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.alarm-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: var(--secondary-background-color, #f5f5f5);
  border-radius: 8px;
  transition: background 0.2s;
}

.alarm-item:hover {
  background: var(--primary-background-color, #e0e0e0);
}

.alarm-item.ringing {
  background: var(--error-color, #f44336);
  color: white;
}

.alarm-item.disabled {
  opacity: 0.6;
}

.alarm-icon {
  font-size: 32px;
  margin-right: 16px;
  color: var(--primary-color);
}

.alarm-item.ringing .alarm-icon {
  color: white;
}

.alarm-icon.shake {
  animation: shake 0.5s ease-in-out infinite;
}

.alarm-info {
  flex: 1;
}

.alarm-time {
  font-size: 24px;
  font-weight: bold;
}

.alarm-name {
  font-size: 14px;
  color: var(--secondary-text-color);
}

.alarm-item.ringing .alarm-name {
  color: rgba(255, 255, 255, 0.9);
}

.alarm-repeat {
  font-size: 12px;
  color: var(--secondary-text-color);
  opacity: 0.8;
}

.alarm-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn:active {
  transform: translateY(0);
}

.btn-add {
  width: 100%;
  background: var(--primary-color);
  color: var(--text-primary-color, #fff);
}

.btn-snooze {
  background: var(--warning-color, #ff9800);
  color: white;
}

.btn-dismiss {
  background: var(--error-color, #f44336);
  color: white;
}

.btn-edit {
  background: var(--secondary-background-color, #e0e0e0);
  color: var(--primary-text-color);
}

.btn-delete {
  background: var(--error-color, #f44336);
  color: white;
}

.btn-save {
  background: var(--primary-color);
  color: var(--text-primary-color, #fff);
}

.btn-cancel {
  background: var(--secondary-background-color, #e0e0e0);
  color: var(--primary-text-color);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--primary-text-color);
  cursor: pointer;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--secondary-background-color, rgba(0, 0, 0, 0.1));
}

.alarm-item.ringing .btn-icon {
  color: white;
}

.alarm-item.ringing .btn-icon:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Toggle */
.toggle {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--disabled-text-color, #ccc);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle input:checked + .toggle-slider {
  background-color: var(--primary-color);
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

/* Add Alarm */
.add-alarm {
  margin-top: 16px;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--card-background-color, #fff);
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--divider-color, #e0e0e0);
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
}

.dialog-content {
  padding: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid var(--divider-color, #e0e0e0);
}

/* Form */
.form-row {
  margin-bottom: 16px;
}

.form-row label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-text-color);
}

.form-row input[type="text"],
.form-row input[type="time"],
.form-row input[type="date"],
.form-row select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--divider-color, #e0e0e0);
  border-radius: 8px;
  font-size: 14px;
  background: var(--card-background-color, #fff);
  color: var(--primary-text-color);
  box-sizing: border-box;
}

.form-row input:focus,
.form-row select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

/* Shake Animation */
@keyframes shake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  10% { transform: translateX(-2px) rotate(-5deg); }
  20% { transform: translateX(2px) rotate(5deg); }
  30% { transform: translateX(-2px) rotate(-5deg); }
  40% { transform: translateX(2px) rotate(5deg); }
  50% { transform: translateX(-1px) rotate(-2deg); }
  60% { transform: translateX(1px) rotate(2deg); }
  70% { transform: translateX(-1px) rotate(-2deg); }
  80% { transform: translateX(1px) rotate(2deg); }
  90% { transform: translateX(0) rotate(0deg); }
}
</style>
