<script setup lang="ts">
import { ref, reactive, watch, toRefs, computed } from 'vue';
import colorName from 'color-name';

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

// Color helpers
const VAR_OPTIONS = [
  'var(--clock-day-bg)',
  'var(--clock-night-bg)',
  'var(--primary-text-color)',
  'var(--primary-color)',
  'var(--error-color)',
  'var(--warning-color)',
];
const COLOR_NAMES = Object.keys(colorName).sort();
const ALL_COLOR_OPTIONS = [...VAR_OPTIONS, ...COLOR_NAMES];

function colorToHex(cssColor: string): string | null {
  try {
    const el = document.createElement('div');
    el.style.color = cssColor;
    document.body.appendChild(el);
    const cs = getComputedStyle(el).color;
    document.body.removeChild(el);
    if (!cs) return null;
    const m = cs.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (!m) return null;
    const r = parseInt(m[1], 10);
    const g = parseInt(m[2], 10);
    const b = parseInt(m[3], 10);
    const hex = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    return hex;
  } catch {
    return null;
  }
}

// Color input state helpers per field
function useColorField(name: string, defaultValue: string) {
  const text = ref(localConfig[name] ?? defaultValue);
  const search = ref('');
  const selected = ref(localConfig[name] ?? '');
  const hex = ref('');

  // initialize hex
  const initHex = colorToHex(text.value);
  if (initHex) hex.value = initHex;

  watch(() => localConfig[name], (v) => {
    text.value = v ?? defaultValue;
    const h = colorToHex(text.value);
    if (h) hex.value = h;
  });

  watch(text, (v) => {
    localConfig[name] = v;
    const h = colorToHex(v);
    if (h) hex.value = h;
  });

  watch(hex, (v) => {
    // when color picker changed, update text
    if (v) {
      text.value = v;
    }
  });

  return { text, search, selected, hex };
}

const bgColor = useColorField('clock_bg_color', 'var(--clock-day-bg)');
const hourColor = useColorField('clock_hour_color', 'var(--primary-text-color)');
const minuteColor = useColorField('clock_minute_color', 'var(--primary-text-color)');
const secondColor = useColorField('clock_second_color', 'var(--primary-color)');
const middleColor = useColorField('clock_middle_color', 'var(--primary-color)');

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
        @value-changed="(e)=> localConfig.entity = e.detail.value || ''"
      />
    </div>

    <div style="display:flex; gap:12px; align-items:flex-start;">
      <div style="flex:1">
        <label style="display:block; margin-bottom:6px; font-weight:500">Clock Display</label>
        <ha-select label="Clock Display" style="width:100%" :value="localConfig.clock_display" @selected="(e)=> localConfig.clock_display = e.target.value">
          <ha-list-item value="analog">Analog</ha-list-item>
          <ha-list-item value="24h">Digital (24h)</ha-list-item>
          <ha-list-item value="12h">Digital (12h)</ha-list-item>
          <ha-list-item value="none">None</ha-list-item>
        </ha-select>
      </div>
    </div>

    <!-- Color inputs: reuse the same layout for each -->
    <div v-for="(field, idx) in [
      {k:'clock_bg_color', label:'Clock Background Color', state:bgColor},
      {k:'clock_hour_color', label:'Clock Hour Color', state:hourColor},
      {k:'clock_minute_color', label:'Clock Minute Color', state:minuteColor},
      {k:'clock_second_color', label:'Clock Second Color', state:secondColor},
      {k:'clock_middle_color', label:'Clock Middle Color', state:middleColor}
    ]" :key="idx">
      <label style="display:block; margin-bottom:6px; font-weight:500">{{field.label}}</label>
      <div style="display:flex; gap:8px; align-items:center">
        <ha-textfield style="flex:1" :value="field.state.text" @input="(e)=> field.state.text = e.target.value" />
        <div style="display:flex; flex-direction:column; gap:6px; width:280px">
          <ha-textfield label="Search Colors" :value="field.state.search" @input="(e)=> field.state.search = e.target.value" />
          <ha-select label="Colors" style="width:100%" @selected="(e)=> { const v=e.target.value; field.state.text = v }">
            <ha-list-item v-for="opt in ALL_COLOR_OPTIONS.filter(o=> !field.state.search || o.toLowerCase().includes(field.state.search.toLowerCase()))" :value="opt" :key="opt">
              <span style="display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid rgba(0,0,0,0.15);background:var(--card-background-color); background-image: none; background: opt;" />
              {{ opt }}
            </ha-list-item>
          </ha-select>
        </div>
        <input type="color" style="width:48px;height:32px;border:none;background:transparent" :value="field.state.hex" @input="(e)=> field.state.hex = e.target.value" />
      </div>
    </div>

    <div style="display:flex; gap:12px; align-items:center">
      <ha-formfield label="Show Seconds on Clock">
        <ha-switch :checked="localConfig.clock_show_seconds !== false" @change="(e)=> localConfig.clock_show_seconds = e.target.checked" />
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
/* Light styling only; the main card styles are in the card SFC */
</style>
