<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import colorName from 'color-name';

const props = defineProps<{
  modelValue?: string;
  label?: string;
}>();
const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void;
}>();

const VAR_OPTIONS = [
  'var(--clock-day-bg)',
  'var(--clock-night-bg)',
  'var(--primary-text-color)',
  'var(--primary-color)',
  'var(--error-color)',
  'var(--warning-color)',
];

const COLOR_NAMES = Object.keys(colorName).sort();
const ALL_OPTIONS = [...VAR_OPTIONS, ...COLOR_NAMES];

const text = ref(props.modelValue ?? '');
const search = ref('');
const hex = ref('');

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
    const hx = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    return hx;
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
  const target = e.target as HTMLSelectElement;
  const val = (target.value as string) || '';
  if (val) {
    text.value = val;
    const h = colorToHex(val);
    if (h) hex.value = h;
  }
}

</script>

<template>
  <div style="display:flex; gap:8px; align-items:center;">
    <ha-textfield :label="props.label || ''" style="flex:1" :value="text" @input="(e)=> text = (e.target as HTMLInputElement).value" />

    <div style="display:flex; flex-direction:column; gap:6px; width:260px">
      <ha-textfield label="Search Colors" :value="search" @input="(e)=> search = (e.target as HTMLInputElement).value" />
      <ha-select label="Colors" style="width:100%" @selected="onSelect">
        <ha-list-item v-for="opt in filteredOptions" :key="opt" :value="opt">
          <span :style="{ display: 'inline-block', width: '12px', height: '12px', marginRight: '8px', border: '1px solid rgba(0,0,0,0.15)', background: opt }"></span>
          {{ opt }}
        </ha-list-item>
      </ha-select>
    </div>

    <input type="color" style="width:48px;height:32px;border:none;background:transparent" :value="hex" @input="(e)=> hex = (e.target as HTMLInputElement).value" />
  </div>
</template>

<style scoped>
/* small tweaks if needed */
</style>
