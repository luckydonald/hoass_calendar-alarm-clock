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
  <div
    style="padding: 16px; display:flex; flex-direction:column; gap:12px;"
  >
    <ha-textfield
      label="Card Title"
      :value="localConfig.title"
      @input="localConfig.title = $event.target.value"
    />
    <!--
    // Entity picker (for single alarm view)
    wrapper.appendChild(this._createEntityPicker());
    -->

    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Entity (optional - for single alarm view)
      </label>
      <ha-entity-picker
        allow-custom-entity
        label="Entity (optional)"
        style="width:100%"
        :value="localConfig.entity"
        :hass="props.hass"
        :includeDomains="['sensor']"
        @value-changed="(e: Event) => localConfig.entity = (e as CustomEvent).detail?.value || ''"
      />
    </div>
    <!--
    // Clock display select
    wrapper.appendChild(this._createSelect(
    -->
    <div
      style="display:flex; gap:12px; align-items:flex-start;"
    >
      <div
        style="flex:1"
      >
        <label
          style="display:block; margin-bottom:6px; font-weight:500"
        >
          Clock Display
        </label>
        <ha-select
          label="Clock Display"
          style="width:100%"
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
    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Background Color
      </label>
      <ColorPicker
        v-model="localConfig.clock_bg_color"
      />
    </div>

    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Hour Color
      </label>
      <ColorPicker
        v-model="localConfig.clock_hour_color"
      />
    </div>

    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Minute Color
      </label>
      <ColorPicker
        v-model="localConfig.clock_minute_color"
      />
    </div>

    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Second Color
      </label>
      <ColorPicker
        v-model="localConfig.clock_second_color"
      />
    </div>

    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Middle (dot/separator) Color
      </label>
      <ColorPicker
        v-model="localConfig.clock_middle_color"
      />
    </div>

    <div
      style="display:flex; gap:12px; align-items:center"
    >
      <ha-formfield
        label="Show Seconds on Clock"
      >
        <ha-switch
          :checked="localConfig.clock_show_seconds !== false"
          @change="(e: Event) => localConfig.clock_show_seconds = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
    </div>

    <div
      style="display:flex; gap:12px; align-items:center"
    >
      <ha-formfield
        label="Smooth Clock Animation (continuous)"
      >
        <ha-switch
          :checked="localConfig.clock_smooth_animation !== false"
          @change="localConfig.clock_animation_mode = (e.target as HTMLInputElement).checked ? 'smooth' : 'ticks'"
        />
      </ha-formfield>
    </div>

    <!--
    // Animation mode selector
    -->
    <!-- Animation mode selector -->
    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Clock Animation Mode
      </label>
      <ha-select
        label="Animation Mode"
        style="width:100%"
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


    <!--
    // Alarm list mode select
    wrapper.appendChild(this._createSelect(
      'alarm_list_mode',
      'Alarm List Mode',
      this._config.alarm_list_mode ?? 'days',
      [
        { value: 'days', label: 'Show alarms for X days' },
        { value: 'count', label: 'Show X alarms' },
      ],
    ));
    -->
    <!-- Alarm list mode (days/count) -->
    <div>
      <label style="display:block; margin-bottom:6px; font-weight:500">Alarm List Mode</label>
      <ha-select
        label="Alarm List Mode"
        style="width:100%"
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
    <!--
    // Alarm list days/count input
    -->
    <!-- Number inputs conditional on mode -->
    <div v-if="localConfig.alarm_list_mode === 'count'">
      <label style="display:block; margin-bottom:6px; font-weight:500">Number of Alarms to Show</label>
      <input type="number" min="1" max="100" style="width:100%; padding:8px;" v-model.number="localConfig.alarm_list_count" />
    </div>
    <div v-else>
      <label style="display:block; margin-bottom:6px; font-weight:500">Days to Show</label>
      <input type="number" min="1" max="365" style="width:100%; padding:8px;" v-model.number="localConfig.alarm_list_days" />
    </div>

    <!--
    // Section visibility toggles
    -->
    <!-- Section visibility toggles -->
    <div
      style="font-weight:500; margin-top:8px"
    >
      Section Visibility
    </div>
    <div
      style="display:flex; gap:12px; flex-direction:column"
    >
      <ha-formfield
        label="Show Clock Section"
      >
        <ha-switch
          :checked="localConfig.show_clock !== false"
          @change="(e: Event) => localConfig.show_clock = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
      <ha-formfield
        label="Show Quick Alarm Section"
      >
        <ha-switch
          :checked="localConfig.show_quick_alarm !== false"
          @change="(e: Event) => localConfig.show_quick_alarm = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
      <ha-formfield
        label="Show Alarm List Section"
      >
        <ha-switch
          :checked="localConfig.show_alarm_list !== false"
          @change="(e: Event) => localConfig.show_alarm_list = (e.target as HTMLInputElement).checked"
        />
      </ha-formfield>
    </div>

    <!--
    // Add section mode
    -->
    <!-- Add section mode -->
    <div>
      <label
        style="display:block; margin-bottom:6px; font-weight:500"
      >
        Add Alarm Section
      </label>
      <ha-select
        label="Add Alarm Section"
        style="width:100%"
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

    <!--
    // Help text
    -->
    <div style="display:flex; gap:8px; justify-content:space-between; align-items:center;">
      <div style="color:inherit; font-size:12px">
        <p style="margin:0 0 8px 0"><strong>List View (default):</strong> Leave entity empty to show all alarms.</p>
        <p style="margin:0"><strong>Single Alarm View:</strong> Select a specific alarm entity to show details for one alarm.</p>
      </div>
    </div>

    <div style="padding: 8px 16px; text-align:right; font-size:12px; color:inherit;">Version: {{ buildVersion }}</div>
  </div>
</template>

<style scoped>
</style>
