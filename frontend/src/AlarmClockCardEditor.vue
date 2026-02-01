<script setup lang="ts">
import { reactive, watch } from 'vue';
import pkg from '../package.json';
import ColorPicker from './ColorPicker.vue';

interface Props {
  hass: any;
  config: Record<string, any>;
  onConfigChanged?: (cfg: Record<string, any>) => void;
}

const props = defineProps<Props>();

const buildVersion = pkg.version || 'unknown';

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

// Values for the clock display select
const clockDisplayOptions = [
  { value: 'analog', label: 'Analog' },
  { value: '24h', label: 'Digital (24h)' },
  { value: '12h', label: 'Digital (12h)' },
  { value: 'none', label: 'None' },
];

const animationModeOptions = [
  { value: 'ticks', label: 'Ticks (discrete)' },
  { value: 'smooth', label: 'Smooth (continuous)' },
  { value: 'db', label: 'DB (delayed stop on 59s)' },
];

const alarmListModeOptions = [
  { value: 'days', label: 'Show alarms for X days' },
  { value: 'count', label: 'Show X alarms' },
];

// Add section mode options
const addSectionOptions = [
  { value: 'auto', label: 'Auto (show when Add clicked)' },
  { value: 'on', label: 'Always show' },
  { value: 'off', label: 'Never show (dialog only)' },
];
</script>

<template>
  <div class="editor-root">
    <ha-textfield
      class="full-width"
      label="Card Title"
      :value="localConfig.title"
      @input="localConfig.title = $event.target.value"
    />

    <div class="field">
      <label class="label">
        Entity (optional - for single alarm view)
      </label>
      <ha-entity-picker
        class="full-width"
        allow-custom-entity
        label="Entity (optional)"
        :value="localConfig.entity"
        :hass="props.hass"
        :include-domains="['sensor']"
        @value-changed="(e: Event) => localConfig.entity = (e as CustomEvent).detail?.value || ''"
      />
    </div>

    <div class="row-flex">
      <div class="col">
        <label class="label">
          Clock Display
        </label>
        <ha-select
          class="full-width"
          label="Clock Display"
          :value="localConfig.clock_display"
          @selected="(e: Event) => localConfig.clock_display = (e.target as HTMLSelectElement).value as any"
        >
          <ha-list-item
            v-for="option in clockDisplayOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </ha-list-item>
        </ha-select>
      </div>
    </div>

    <!-- Color inputs: use ColorPicker component -->
    <div class="field">
      <label class="label">
        Clock Background Color
      </label>
      <ColorPicker v-model="localConfig.clock_bg_color" />
    </div>

    <div class="field">
      <label class="label">
        Clock Hour Color
      </label>
      <ColorPicker v-model="localConfig.clock_hour_color" />
    </div>

    <div class="field">
      <label class="label">
        Clock Minute Color
      </label>
      <ColorPicker v-model="localConfig.clock_minute_color" />
    </div>

    <div class="field">
      <label class="label">Clock Second Color</label>
      <ColorPicker v-model="localConfig.clock_second_color" />
    </div>

    <div class="field">
      <label class="label">Clock Middle (dot/separator) Color</label>
      <ColorPicker v-model="localConfig.clock_middle_color" />
    </div>

    <div class="inline-field">
      <ha-formfield label="Show Seconds on Clock">
        <ha-switch
          :checked="localConfig.clock_show_seconds !== false"
          @change="(e: Event) => localConfig.clock_show_seconds = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
    </div>

    <!-- Animation mode selector -->
    <div class="field">
      <label class="label">Clock Animation Mode</label>
      <ha-select
        class="full-width"
        label="Animation Mode"
        :value="localConfig.clock_animation_mode"
        @selected="(e: Event) => localConfig.clock_animation_mode = (e.target as HTMLSelectElement).value as any"
      >
        <ha-list-item
          v-for="opt in animationModeOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </ha-list-item>
      </ha-select>
    </div>

    <!-- Alarm list mode (days/count) -->
    <div class="field">
      <label class="label">Alarm List Mode</label>
      <ha-select
        class="full-width"
        label="Alarm List Mode"
        :value="localConfig.alarm_list_mode"
        @selected="(e: Event) => localConfig.alarm_list_mode = (e.target as HTMLSelectElement).value as any"
      >
        <ha-list-item
          v-for="opt in alarmListModeOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </ha-list-item>
      </ha-select>
    </div>

    <!-- Number inputs conditional on mode -->
    <div
      v-if="localConfig.alarm_list_mode === 'count'"
      class="field"
    >
      <label class="label">Number of Alarms to Show</label>
      <input
        v-model.number="localConfig.alarm_list_count"
        class="number-input full-width"
        type="number"
        min="1"
        max="100"
      />
    </div>
    <div
      v-else
      class="field"
    >
      <label class="label">Days to Show</label>
      <input
        v-model.number="localConfig.alarm_list_days"
        class="number-input full-width"
        type="number"
        min="1"
        max="365"
      />
    </div>

    <!-- Section visibility toggles -->
    <div class="section-header">
      Section Visibility
    </div>
    <div class="section-toggles">
      <ha-formfield label="Show Clock Section">
        <ha-switch
          :checked="localConfig.show_clock !== false"
          @change="(e: Event) => localConfig.show_clock = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
      <ha-formfield label="Show Quick Alarm Section">
        <ha-switch
          :checked="localConfig.show_quick_alarm !== false"
          @change="(e: Event) => localConfig.show_quick_alarm = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
      <ha-formfield label="Show Alarm List Section">
        <ha-switch
          :checked="localConfig.show_alarm_list !== false"
          @change="(e: Event) => localConfig.show_alarm_list = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
    </div>

    <!-- Add section mode -->
    <div class="field">
      <label class="label">Add Alarm Section</label>
      <ha-select
        class="full-width"
        label="Add Alarm Section"
        :value="localConfig.show_add_section"
        @selected="(e: Event) => localConfig.show_add_section = (e.target as HTMLSelectElement).value as any"
      >
        <ha-list-item
          v-for="opt in addSectionOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </ha-list-item>
      </ha-select>
    </div>

    <!-- Help text -->
    <div class="help-row">
      <div class="help-text">
        <p><strong>List View (default):</strong> Leave entity empty to show all alarms.</p>
        <p><strong>Single Alarm View:</strong> Select a specific alarm entity to show details for one alarm.</p>
      </div>
    </div>

    <div class="version">
      Version: {{ buildVersion }}
    </div>
  </div>
</template>

<style scoped lang="scss">
.editor-root {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.full-width {
  width: 100%;
}

.row-flex {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.col {
  flex: 1;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.inline-field {
  display: flex;
  gap: 12px;
  align-items: center;
}

.number-input {
  padding: 8px;
  box-sizing: border-box;
}

.section-header {
  font-weight: 500;
  margin-top: 8px;
}

.section-toggles {
  display: flex;
  gap: 12px;
  flex-direction: column;
}

.help-row {
  display: flex;
  gap: 8px;
  justify-content: space-between;
  align-items: center;
}

.help-text {
  color: inherit;
  font-size: 12px;
  p { margin: 0 0 8px 0; }
}

.version {
  padding: 8px 16px;
  text-align: right;
  font-size: 12px;
  color: inherit;
}
</style>
