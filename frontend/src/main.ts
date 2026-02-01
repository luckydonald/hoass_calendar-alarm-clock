import {
  createApp,
  h,
} from 'vue';

import pkg from '../package.json';
import AlarmClockCard from './AlarmClockCard.vue';
import AlarmClockCardEditor from './AlarmClockCardEditor.vue';

import type { App, ComponentPublicInstance } from 'vue';

import type {
  CardConfig, HomeAssistant, MountedWrapperExtras, Wrapper,
} from './types';

interface AlarmClockCardConfig extends CardConfig {
  type?: string;
  // UI/editor related optional properties
  title?: string;
  entity?: string;
  clock_display?: string;
  alarm_list_mode?: 'days' | 'count';
  alarm_list_count?: number;
  alarm_list_days?: number;
  show_clock?: boolean;
  show_quick_alarm?: boolean;
  show_alarm_list?: boolean;
  show_add_section?: string;
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

  public static getConfigElement(): HTMLElement {
    // Create a wrapper element and mount the Vue editor into it.
    // Define 'hass' and 'setConfig' on the element so Home Assistant can safely set properties.
    const wrapper: Wrapper<AlarmClockCardConfig> = document.createElement('div');

    // Mount the Vue editor into the wrapper. Keep a reference to the VM proxy so we can update props.

    const app = createApp(AlarmClockCardEditor, {
      hass: null,
      config: {},
      onConfigChanged: (cfg: AlarmClockCardConfig) => {
        // When the editor notifies of config changes, dispatch an event from the wrapper so HA picks it up
        const event = new CustomEvent('config-changed', {
          detail: { config: cfg },
          bubbles: true,
          composed: true,
        });
        wrapper.dispatchEvent(event);
      },
    });

    // noinspection UnnecessaryLocalVariableJS
    const vmOrigForTyping = app.mount(wrapper);
    const vm = vmOrigForTyping as typeof vmOrigForTyping & MountedWrapperExtras<AlarmClockCardConfig>;

    // Define a 'hass' property so HA can set it (and we forward it to the Vue component proxy)
    Object.defineProperty(wrapper, 'hass', {
      configurable: true,
      enumerable: true,
      set(hass: HomeAssistant) {
        try {
          if (vm) vm.hass = hass;
        } catch {
          // ignore errors setting on vm
        }
      },
      get(): HomeAssistant | null {
        return vm?.hass ?? null;
      },
    });

    // Provide a setConfig method which HA uses to initialize the editor
    wrapper.setConfig = (config: AlarmClockCardConfig) => {
      try {
        if (vm) vm.config = config;
      } catch {
        // ignore
      }
    };

    return wrapper;
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
      clock_animation_mode: 'smooth',
    };
  }
}

class AlarmClockCardEditor extends HTMLElement {
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
        return h(AlarmClockCardEditor, {
          hass: data.hass,
          config: data.config,
          onConfigChanged: (cfg: AlarmClockCardConfig) => {
            this._updateConfig(cfg);
          },
        });
      },
    });

    row.appendChild(labelEl);
    row.appendChild(input);
    return row;
  }

  private _createSelect(
    name: string,
    label: string,
    value: string,
    options: {
      value: string;
      label: string;
    }[],
  ): HTMLDivElement {
    const row = document.createElement('div');

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.style.display = 'block';
    labelEl.style.marginBottom = '4px';
    labelEl.style.fontWeight = '500';
    labelEl.style.color = 'var(--primary-text-color)';

    const select = document.createElement('ha-select') as HTMLSelectElement;
    select.setAttribute('label', label);
    select.style.width = '100%';

    options.forEach((opt) => {
      const optionEl = document.createElement('mwc-list-item');
      optionEl.setAttribute('value', opt.value);
      optionEl.textContent = opt.label;
      if (opt.value === value) {
        optionEl.setAttribute('selected', '');
      }
      select.appendChild(optionEl);
    });

    this._app.mount(this._root);
  }

  public disconnectedCallback(): void {
    if (this._app) {
      this._app.unmount();
      this._app = null;
    }
  }

  private _updateConfig(update: Partial<AlarmClockCardConfig>): void {
    this._config = {
      ...this._config,
      ...update,
    };
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

// Register with Home Assistant's custom card registry
window.customCards = window.customCards ?? [];
window.customCards.push({
  type: 'calendar-alarm-clock-card',
  name: 'Calendar based Alarm Clock Card',
  description: 'A card for managing calendar-based alarms with clock display, quick alarms, snooze and dismiss',
  preview: true,
  version: pkg.version || 'dev',
});

// eslint-disable-next-line no-console
console.info(
  `%c CALENDAR-ALARM-CLOCK-CARD %c ${pkg.version || 'dev'}`,
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;',
);
