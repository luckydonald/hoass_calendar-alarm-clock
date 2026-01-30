<script setup lang="ts">
import colorName from 'color-name';
import { computed, onMounted, ref, watch } from 'vue';

const props = defineProps<{
  modelValue?: string;
  label?: string;
}>();
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void; }>();

const VAR_OPTIONS = [
  'var(--clock-day-bg)',
  'var(--clock-night-bg)',
  'var(--primary-text-color)',
  'var(--primary-color)',
  'var(--error-color)',
  'var(--warning-color)',
];

const COLOR_NAMES = Object.keys(colorName).sort();
const ALL_OPTIONS = [
  ...VAR_OPTIONS,
  ...COLOR_NAMES,
];

const text = ref(props.modelValue ?? '');
const search = ref('');
const hex = ref('');

function colorToHex(cssColor: string): string | null {
  try {
    const el = document.createElement('div');
    el.style.color = cssColor;
    // Make sure element is not visible
    el.style.position = 'fixed';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    const cs = getComputedStyle(el).color;
    document.body.removeChild(el);
    if (!cs) return null;
    const m = cs.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (!m) return null;
    const r = parseInt(m[1], 10);
    const g = parseInt(m[2], 10);
    const b = parseInt(m[3], 10);
    // eslint-disable-next-line no-bitwise
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  } catch {
    return null;
  }
}

// Initialize
onMounted(() => {
  text.value = props.modelValue ?? '';
  const h = colorToHex(text.value);
  if (h) hex.value = h;
});

watch(() => props.modelValue, (v) => {
  text.value = v ?? '';
  const h = colorToHex(text.value);
  if (h) hex.value = h;
}, { immediate: true });

watch(text, (v) => {
  emit('update:modelValue', v ?? '');
  const h = colorToHex(v ?? '');
  if (h) hex.value = h;
});

watch(hex, (v) => {
  if (v) {
    // hex -> text
    text.value = v;
  }
});

const filteredOptions = computed(() => {
  const f = (search.value || '').trim().toLowerCase();
  if (!f) return ALL_OPTIONS;
  return ALL_OPTIONS.filter((o) => o.toLowerCase().includes(f));
});

function onSelect(e: Event) {
  const target = e.target as HTMLSelectElement | HTMLElement | any;
  // ha-select/ha-list-item may provide value in different places; try common ones
  const val = (target && (target.value ?? target.getAttribute?.('value'))) as string || '';
  if (val) {
    text.value = val;
    const h = colorToHex(val);
    if (h) hex.value = h;
  }
}

function onTextInput(e: Event) {
  const targ = e.target as HTMLInputElement;
  text.value = targ.value;
}

function onSearchInput(e: Event) {
  const targ = e.target as HTMLInputElement;
  search.value = targ.value;
}

function onColorInput(e: Event) {
  const targ = e.target as HTMLInputElement;
  hex.value = targ.value;
}
</script>

<template>
  <div class="colorpicker-root">
    <ha-textfield
      :label="props.label || ''"
      class="text-field-flex"
      :value="text"
      @input="onTextInput"
    />

    <div class="selector-panel">
      <ha-textfield
        label="Search Colors"
        :value="search"
        @input="onSearchInput"
      />

      <ha-select
        label="Colors"
        class="full-width"
        @selected="onSelect"
      >
        <ha-list-item
          v-for="opt in filteredOptions"
          :key="opt"
          :value="opt"
        >
          <!-- Use a simple color square instead of SVG to ensure CSS variables and named colors render correctly -->
          <span
            class="color-swatch"
            :style="{ background: opt }"
          />

          {{ opt }}
        </ha-list-item>
      </ha-select>
    </div>

    <input
      type="color"
      class="color-input"
      :value="hex"
      @input="onColorInput"
    />
  </div>
</template>

<style scoped>
.colorpicker-root {
  display: flex;
  gap: 8px;
  align-items: center;
}

.text-field-flex {
  flex: 1;
}

.selector-panel {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 260px;
}

.full-width {
  width: 100%;
}

.color-swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 8px;
  vertical-align: middle;
  border: 1px solid rgba(0,0,0,0.15);
}

.color-input {
  width: 48px;
  height: 32px;
  border: none;
  background: transparent;
}
</style>
