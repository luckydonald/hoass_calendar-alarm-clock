import colorName from 'color-name';
import { type App, type ComponentPublicInstance, createApp, h } from 'vue';
import AlarmClockCard from './AlarmClockCard.vue';
import AlarmClockCardEditorVue from './AlarmClockCardEditor.vue';
import type { CardConfig, HomeAssistant } from './types';
import pkg from '../package.json';

interface AlarmClockCardConfig extends CardConfig {
  type?: string;
}

interface AppData {
  hass: HomeAssistant | null;
  config: AlarmClockCardConfig;
}

class AlarmClockCardElement extends HTMLElement {
  private _config: AlarmClockCardConfig = {};
  private _hass: HomeAssistant | null = null;
  private _app: App | null = null;
  private _root: HTMLDivElement | null = null;

  public set hass(hass: HomeAssistant) {
    this._hass = hass;
    if (this._app?._instance?.proxy) {
      const proxy = this._app._instance.proxy as ComponentPublicInstance & AppData;
      proxy.hass = hass;
    }
  }

  public setConfig(config: AlarmClockCardConfig): void {
    this._config = config;
    if (this._app?._instance?.proxy) {
      const proxy = this._app._instance.proxy as ComponentPublicInstance & AppData;
      proxy.config = config;
    }
  }

  public connectedCallback(): void {
    if (!this._root) {
      this._root = document.createElement('div');
      this.appendChild(this._root);
    }

    const initialHass = this._hass;
    const initialConfig = this._config;

    this._app = createApp({
      data(): AppData {
        return {
          hass: initialHass,
          config: initialConfig,
        };
      },
      render() {
        const data = this as unknown as AppData;
        return h(AlarmClockCard, {
          hass: data.hass,
          config: data.config,
        });
      },
    });

    this._app.mount(this._root);
  }

  public disconnectedCallback(): void {
    if (this._app) {
      this._app.unmount();
      this._app = null;
    }
  }

  public getCardSize(): number {
    return 4;
  }

  public static getConfigElement(): AlarmClockCardEditor {
    return document.createElement('calendar-alarm-clock-card-editor') as AlarmClockCardEditor;
  }

  public static getStubConfig(): AlarmClockCardConfig {
    return {
      type: 'custom:calendar-alarm-clock-card',
      title: 'Calendar backed Alarm Clock',
      clock_display: 'analog',
      alarm_list_mode: 'days',
      alarm_list_days: 7,
      show_clock: true,
      show_quick_alarm: true,
      show_alarm_list: true,
      show_add_section: 'auto',
      clock_bg_color: 'var(--clock-day-bg)',
      clock_hour_color: 'var(--primary-text-color)',
      clock_minute_color: 'var(--primary-text-color)',
      clock_second_color: 'var(--primary-color)',
      clock_middle_color: 'var(--primary-color)',
      clock_show_seconds: true,
      clock_smooth_animation: true,
    };
  }
}

class AlarmClockCardEditor extends HTMLElement {
  private _config: AlarmClockCardConfig = {};
  private _hass: HomeAssistant | null = null;
  private _appRoot: HTMLDivElement | null = null;
  private _vueApp: App | null = null;

  public set hass(hass: HomeAssistant) {
    this._hass = hass;
    this._render();
  }

  public setConfig(config: AlarmClockCardConfig): void {
    this._config = config;
    this._render();
  }

  private _render(): void {
    if (!this._hass) return;

    // Use Vue component mounting for the editor to avoid DOM re-creation problems
    if (!this._appRoot) {
      this._appRoot = document.createElement('div');
      this.appendChild(this._appRoot);
    }

    if (this._vueApp) {
      // update props via component instance
      const root = this._vueApp._instance?.proxy as any;
      if (root) {
        root.hass = this._hass;
        root.config = this._config;
      }
      return;
    }

    this._vueApp = createApp(AlarmClockCardEditorVue, {
      hass: this._hass,
      config: this._config,
      onConfigChanged: (cfg: AlarmClockCardConfig) => {
        this._updateConfig(cfg);
      },
    });

    this._vueApp.mount(this._appRoot);
  }

  private _updateConfig(update: Partial<AlarmClockCardConfig>): void {
    this._config = { ...this._config, ...update };
    this._fireConfigChanged();
  }

  private _fireConfigChanged(): void {
    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

// Register custom elements
customElements.define('calendar-alarm-clock-card', AlarmClockCardElement);
customElements.define('calendar-alarm-clock-card-editor', AlarmClockCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'calendar-alarm-clock-card',
  name: 'Calendar based Alarm Clock Card',
  description: 'A card for managing calendar-based alarms with clock display, quick alarms, snooze and dismiss',
  preview: true,
  version: pkg.version || 'dev',
});

console.info(
  '%c CALENDAR-ALARM-CLOCK-CARD %c ' + (pkg.version || 'dev'),
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;',
);
