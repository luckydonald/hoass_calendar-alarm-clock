import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // Treat all tags with a dash as custom elements
          isCustomElement: (tag) => tag.includes('-') && !tag.startsWith('v-'),
        },
      },
    }),
  ],
  define: {
    'process.env': {},
  },
  build: {
    lib: {
      entry: resolve(__dirname, 'src/main.js'),
      name: 'AlarmClockCard',
      fileName: () => 'alarm-clock-card.js',
      formats: ['iife'],
    },
    outDir: '../custom_components/calendar_alarm_clock/www',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        globals: {},
      },
    },
  },
});

