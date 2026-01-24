<script setup lang="ts">
import colorName from 'color-name';
import { computed, reactive, ref, toRefs, watch } from 'vue';
import ColorPicker from './ColorPicker.vue';

interface Props {
  hass: any;
  config: Record<string, any>;
  onConfigChanged?: (cfg: Record<string, any>) => void;
}

const props = defineProps<Props>();

const emitConfig = (cfg: Record<string, any>) => {
  if (props.onConfigChanged) props.onConfigChanged(cfg);
};

// Local reactive copy of config
const localConfig = reactive({ ...(props.config || {}) });

// Keep in sync when parent updates config
watch(() => props.config, (v) => {
  if (!v) return;
  Object.assign(localConfig, v);
}, { deep: true });

// Whenever localConfig changes, call onConfigChanged
watch(localConfig, (v) => {
  emitConfig({ ...(v as Record<string, any>) });
}, { deep: true });

// Helpers for selects
const clockDisplayOptions = [
  { value: 'analog', label: 'Analog' },
  { value: '24h', label: 'Digital (24h)' },
  { value: '12h', label: 'Digital (12h)' },
  { value: 'none', label: 'None' },
];

const alarmListModeOptions = [
  { value: 'days', label: 'Show alarms for X days' },
  { value: 'count', label: 'Show X alarms' },
];

// Typed event handlers used by the template
function onEntityValueChanged(e: Event) {
  // Home Assistant entity-picker dispatches a CustomEvent with detail.value
  const ev = e as CustomEvent;
  localConfig.entity = ev.detail?.value || '';
}

function onClockDisplaySelected(e: Event) {
  const targ = e.target as HTMLSelectElement;
  localConfig.clock_display = targ.value as any;
}

function onShowSecondsChange(e: Event) {
  const targ = e.target as HTMLInputElement;
  localConfig.clock_show_seconds = targ.checked;
}

function onSmoothChange(e: Event) {
  const targ = e.target as HTMLInputElement;
  localConfig.clock_smooth_animation = targ.checked;
}
</script>

<template>
  <div style="padding: 16px; display:flex; flex-direction:column; gap:12px;">
    <ha-textfield
      label="Card Title"
      :value="localConfig.title"
      @input="localConfig.title = $event.target.value"
    />

    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Entity (optional - for single alarm view)</label>
      <ha-entity-picker
        allow-custom-entity
        label="Entity (optional)"
        style="width:100%"
        :value="localConfig.entity"
        :hass="props.hass"
        :includeDomains="['sensor']"
        @value-changed="onEntityValueChanged"
      />
    </div>

    <div style="display:flex; gap:12px; align-items:flex-start;">
      <div style="flex:1">
        <label style="display:block; margin-bottom:6px; font-weight:500">Clock Display</label>
        <ha-select label="Clock Display" style="width:100%" :value="localConfig.clock_display" @selected="onClockDisplaySelected">
          <ha-list-item value="analog">Analog</ha-list-item>
          <ha-list-item value="24h">Digital (24h)</ha-list-item>
          <ha-list-item value="12h">Digital (12h)</ha-list-item>
          <ha-list-item value="none">None</ha-list-item>
        </ha-select>
      </div>
    </div>

    <!-- Color inputs: use ColorPicker component -->
    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Clock Background Color</label>
      <ColorPicker v-model="localConfig.clock_bg_color" />
    </div>

    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Clock Hour Color</label>
      <ColorPicker v-model="localConfig.clock_hour_color" />
    </div>

    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Clock Minute Color</label>
      <ColorPicker v-model="localConfig.clock_minute_color" />
    </div>

    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Clock Second Color</label>
      <ColorPicker v-model="localConfig.clock_second_color" />
    </div>

    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Clock Middle (dot/separator) Color</label>
      <ColorPicker v-model="localConfig.clock_middle_color" />
    </div>

    <div style="display:flex; gap:12px; align-items:center">
      <ha-formfield label="Show Seconds on Clock">
        <ha-switch :checked="localConfig.clock_show_seconds !== false" @change="onShowSecondsChange" />
      </ha-formfield>
    </div>

    <div style="display:flex; gap:12px; align-items:center">
      <ha-formfield label="Smooth Clock Animation (continuous)">
        <ha-switch :checked="localConfig.clock_smooth_animation !== false" @change="onSmoothChange" />
      </ha-formfield>
    </div>

    <div style="display:flex; gap:8px; justify-content:space-between; align-items:center;">
      <div style="color:var(--secondary-text-color); font-size:12px">
        <p style="margin:0 0 8px 0"><strong>List View (default):</strong> Leave entity empty to show all alarms.</p>
        <p style="margin:0"><strong>Single Alarm View:</strong> Select a specific alarm entity to show details for one alarm.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
