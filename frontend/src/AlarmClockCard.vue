<template>
  <ha-card :header="cardTitle">
    <div class="card-content">
      <!-- Header with next alarm -->
      <div class="next-alarm-header" v-if="nextAlarm && !isSingleAlarmView">
        <div class="next-alarm-icon" :class="{ ringing: isNextAlarmRinging }">
          <ha-icon icon="mdi:alarm"></ha-icon>
        </div>
        <div class="next-alarm-info">
          <div class="next-alarm-label">Next Alarm</div>
          <div class="next-alarm-time">{{ formatTime(nextAlarm.time) }}</div>
          <div class="next-alarm-name">{{ nextAlarm.name }}</div>
        </div>
      </div>

      <!-- Single Alarm View -->
      <div v-if="isSingleAlarmView && selectedAlarm" class="single-alarm-view">
        <div class="single-alarm-icon" :class="{ ringing: isAlarmRinging(selectedAlarm), disabled: !selectedAlarm.enabled }">
          <ha-icon :icon="getAlarmIcon(selectedAlarm)"></ha-icon>
        </div>
        <div class="single-alarm-time">{{ formatTime(selectedAlarm.time) }}</div>
        <div class="single-alarm-name">{{ selectedAlarm.name }}</div>
        <div class="single-alarm-status">{{ getStatusText(selectedAlarm) }}</div>

        <div class="single-alarm-actions" v-if="isAlarmRinging(selectedAlarm)">
          <button class="btn btn-snooze" @click="snoozeAlarm(selectedAlarm)">
            <ha-icon icon="mdi:alarm-snooze"></ha-icon>
            Snooze
          </button>
          <button class="btn btn-dismiss" @click="dismissAlarm(selectedAlarm)">
            <ha-icon icon="mdi:alarm-off"></ha-icon>
            Dismiss
          </button>
        </div>

        <div class="single-alarm-toggle" v-else>
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
          <div class="detail-row" v-if="selectedAlarm.snooze_count > 0">
            <span class="detail-label">Snooze Count:</span>
            <span class="detail-value">{{ selectedAlarm.snooze_count }}</span>
          </div>
        </div>

        <div class="single-alarm-buttons">
          <button class="btn btn-edit" @click="openEditDialog(selectedAlarm)">
            <ha-icon icon="mdi:pencil"></ha-icon>
            Edit
          </button>
          <button class="btn btn-delete" @click="deleteAlarm(selectedAlarm)">
            <ha-icon icon="mdi:delete"></ha-icon>
            Delete
          </button>
        </div>
      </div>

      <!-- Alarm List View -->
      <div v-else class="alarm-list">
        <div v-if="alarms.length === 0" class="no-alarms">
          <ha-icon icon="mdi:alarm-plus"></ha-icon>
          <p>No alarms scheduled</p>
        </div>

        <div
          v-for="alarm in sortedAlarms"
          :key="alarm.id"
          class="alarm-item"
          :class="{ ringing: isAlarmRinging(alarm), disabled: !alarm.enabled }"
        >
          <div class="alarm-icon" :class="{ shake: isAlarmRinging(alarm) }">
            <ha-icon :icon="getAlarmIcon(alarm)"></ha-icon>
          </div>

          <div class="alarm-info">
            <div class="alarm-time">{{ formatTime(alarm.time) }}</div>
            <div class="alarm-name">{{ alarm.name }}</div>
            <div class="alarm-repeat" v-if="alarm.repeat !== 'none'">
              {{ formatRepeat(alarm.repeat) }}
            </div>
          </div>

          <div class="alarm-actions">
            <template v-if="isAlarmRinging(alarm)">
              <button class="btn-icon" @click="snoozeAlarm(alarm)" title="Snooze">
                <ha-icon icon="mdi:alarm-snooze"></ha-icon>
              </button>
              <button class="btn-icon" @click="dismissAlarm(alarm)" title="Dismiss">
                <ha-icon icon="mdi:alarm-off"></ha-icon>
              </button>
            </template>
            <template v-else>
              <label class="toggle">
                <input type="checkbox" :checked="alarm.enabled" @change="toggleAlarm(alarm)" />
                <span class="toggle-slider"></span>
              </label>
              <button class="btn-icon" @click="openEditDialog(alarm)" title="Edit">
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="btn-icon" @click="deleteAlarm(alarm)" title="Delete">
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Add Alarm Button -->
      <div class="add-alarm" v-if="!isSingleAlarmView">
        <button class="btn btn-add" @click="openAddDialog">
          <ha-icon icon="mdi:plus"></ha-icon>
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
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="dialog-content">
          <div class="form-row">
            <label>Name</label>
            <input type="text" v-model="dialogData.name" placeholder="Alarm" />
          </div>
          <div class="form-row">
            <label>Time</label>
            <input type="time" v-model="dialogData.time" />
          </div>
          <div class="form-row">
            <label>Date</label>
            <input type="date" v-model="dialogData.date" />
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
              <input type="checkbox" v-model="dialogData.enabled" />
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

<script>
export default {
  name: 'AlarmClockCard',
  props: {
    hass: {
      type: Object,
      default: null,
    },
    config: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      showDialog: false,
      isEditing: false,
      editingAlarmId: null,
      dialogData: {
        name: 'Alarm',
        time: '07:00',
        date: '',
        repeat: 'none',
        enabled: true,
      },
    };
  },
  computed: {
    cardTitle() {
      return this.config.title || 'Alarm Clock';
    },
    isSingleAlarmView() {
      return !!this.config.entity;
    },
    alarms() {
      if (!this.hass) return [];

      const alarms = [];
      const states = this.hass.states;

      for (const entityId in states) {
        const state = states[entityId];
        if (entityId.startsWith('sensor.') &&
            state.attributes.alarm_id &&
            !entityId.includes('_next_alarm') &&
            !entityId.includes('_previous_alarm')) {
          alarms.push({
            entity_id: entityId,
            id: state.attributes.alarm_id,
            name: state.attributes.name || 'Alarm',
            time: state.attributes.time,
            enabled: state.attributes.enabled !== false,
            repeat: state.attributes.repeat || 'none',
            snooze_count: state.attributes.snooze_count || 0,
            state: state.state,
          });
        }
      }

      return alarms;
    },
    sortedAlarms() {
      return [...this.alarms].sort((a, b) => {
        const timeA = new Date(a.time).getTime();
        const timeB = new Date(b.time).getTime();
        return timeA - timeB;
      });
    },
    selectedAlarm() {
      if (!this.config.entity || !this.hass) return null;

      const state = this.hass.states[this.config.entity];
      if (!state) return null;

      return {
        entity_id: this.config.entity,
        id: state.attributes.alarm_id,
        name: state.attributes.name || 'Alarm',
        time: state.attributes.time,
        enabled: state.attributes.enabled !== false,
        repeat: state.attributes.repeat || 'none',
        snooze_count: state.attributes.snooze_count || 0,
        state: state.state,
      };
    },
    nextAlarm() {
      if (!this.hass) return null;

      // Find the next_alarm sensor
      for (const entityId in this.hass.states) {
        if (entityId.includes('_next_alarm')) {
          const state = this.hass.states[entityId];
          if (state.state && state.state !== 'unknown') {
            return {
              time: state.attributes.time,
              name: state.attributes.name || 'Alarm',
              state: state.attributes.state,
            };
          }
        }
      }

      return null;
    },
    isNextAlarmRinging() {
      return this.nextAlarm &&
        (this.nextAlarm.state === 'ringing' || this.nextAlarm.state === 'ringing_snooze');
    },
  },
  methods: {
    formatTime(isoTime) {
      if (!isoTime) return '--:--';
      try {
        const date = new Date(isoTime);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch {
        return isoTime;
      }
    },
    formatRepeat(repeat) {
      const labels = {
        none: 'Once',
        daily: 'Daily',
        weekdays: 'Weekdays',
        weekends: 'Weekends',
        weekly: 'Weekly',
      };
      return labels[repeat] || repeat;
    },
    getAlarmIcon(alarm) {
      if (this.isAlarmRinging(alarm)) return 'mdi:alarm-note';
      if (alarm.state === 'snoozed') return 'mdi:alarm-snooze';
      if (!alarm.enabled) return 'mdi:alarm-off';
      return 'mdi:alarm';
    },
    getStatusText(alarm) {
      const states = {
        before: 'Scheduled',
        ringing: '🔔 Ringing!',
        ringing_snooze: '🔔 Ringing (Snoozed)!',
        snoozed: 'Snoozed',
        dismissed: 'Dismissed',
        timed_out: 'Timed Out',
      };
      return states[alarm.state] || alarm.state;
    },
    isAlarmRinging(alarm) {
      return alarm.state === 'ringing' || alarm.state === 'ringing_snooze';
    },
    async toggleAlarm(alarm) {
      if (!this.hass) return;

      const service = alarm.enabled ? 'disable_alarm' : 'enable_alarm';
      await this.hass.callService('calendar_alarm_clock', service, {
        alarm_id: alarm.id,
      });
    },
    async snoozeAlarm(alarm) {
      if (!this.hass) return;

      await this.hass.callService('calendar_alarm_clock', 'snooze_alarm', {
        alarm_id: alarm.id,
      });
    },
    async dismissAlarm(alarm) {
      if (!this.hass) return;

      await this.hass.callService('calendar_alarm_clock', 'dismiss_alarm', {
        alarm_id: alarm.id,
      });
    },
    async deleteAlarm(alarm) {
      if (!this.hass) return;

      if (confirm(`Delete alarm "${alarm.name}"?`)) {
        await this.hass.callService('calendar_alarm_clock', 'delete_alarm', {
          alarm_id: alarm.id,
        });
      }
    },
    openAddDialog() {
      this.isEditing = false;
      this.editingAlarmId = null;
      this.dialogData = {
        name: 'Alarm',
        time: '07:00',
        date: new Date().toISOString().split('T')[0],
        repeat: 'none',
        enabled: true,
      };
      this.showDialog = true;
    },
    openEditDialog(alarm) {
      this.isEditing = true;
      this.editingAlarmId = alarm.id;

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

      this.dialogData = {
        name: alarm.name,
        time: time,
        date: date,
        repeat: alarm.repeat,
        enabled: alarm.enabled,
      };
      this.showDialog = true;
    },
    closeDialog() {
      this.showDialog = false;
    },
    async saveAlarm() {
      if (!this.hass) return;

      if (this.isEditing) {
        await this.hass.callService('calendar_alarm_clock', 'edit_alarm', {
          alarm_id: this.editingAlarmId,
          name: this.dialogData.name,
          time: this.dialogData.time,
          repeat: this.dialogData.repeat,
          enabled: this.dialogData.enabled,
        });
      } else {
        await this.hass.callService('calendar_alarm_clock', 'create_alarm', {
          name: this.dialogData.name,
          time: this.dialogData.time,
          date: this.dialogData.date,
          repeat: this.dialogData.repeat,
          enabled: this.dialogData.enabled,
        });
      }

      this.closeDialog();
    },
  },
};
</script>

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

