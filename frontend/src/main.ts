import { createApp, h, type App, type Component } from 'vue';
import AlarmClockCard from './AlarmClockCard.vue';

interface AlarmClockCardConfig {
  type?: string;
  entity?: string;
  title?: string;
}

class AlarmClockCardElement extends HTMLElement {
  private _config: AlarmClockCardConfig = {};
  private _hass: HomeAssistant | null = null;
  private _app: App | null = null;
  private _root: HTMLDivElement | null = null;

  set hass(hass: HomeAssistant) {
    this._hass = hass;
    if (this._app?._instance?.proxy) {
      (this._app._instance.proxy as { hass: HomeAssistant }).hass = hass;
    }
  }

  setConfig(config: AlarmClockCardConfig): void {
    this._config = config;
    if (this._app?._instance?.proxy) {
      (this._app._instance.proxy as { config: AlarmClockCardConfig }).config = config;
    }
  }

  connectedCallback(): void {
    if (!this._root) {
      this._root = document.createElement('div');
      this.appendChild(this._root);
    }

    const hass = this._hass;
    const config = this._config;

    this._app = createApp({
      data() {
        return {
          hass: hass as HomeAssistant | null,
          config: config as AlarmClockCardConfig,
        };
      },
      render() {
        return h(AlarmClockCard as Component, {
          hass: this.hass,
          config: this.config,
        });
      },
    });

    this._app.mount(this._root);
  }

  disconnectedCallback(): void {
    if (this._app) {
      this._app.unmount();
      this._app = null;
    }
  }

  getCardSize(): number {
    return 3;
  }

  static getConfigElement(): HTMLElement {
    return document.createElement('alarm-clock-card-editor');
  }

  static getStubConfig(): AlarmClockCardConfig {
    return {
      entity: '',
      title: 'Alarm Clock',
    };
  }
}

class AlarmClockCardEditor extends HTMLElement {
  private _config: AlarmClockCardConfig = {};
  private _hass: HomeAssistant | null = null;

  set hass(hass: HomeAssistant) {
    this._hass = hass;
  }

  setConfig(config: AlarmClockCardConfig): void {
    this._config = config;
    this._render();
  }

  private _render(): void {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    this.shadowRoot!.innerHTML = `
      <style>
        .form-row {
          margin-bottom: 16px;
        }
        label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
        }
        input, select {
          width: 100%;
          padding: 8px;
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color, #000);
          box-sizing: border-box;
        }
      </style>
      <div class="form-row">
        <label>Entity (optional, for single alarm view)</label>
        <input type="text" id="entity" value="${this._config.entity || ''}" />
      </div>
      <div class="form-row">
        <label>Title</label>
        <input type="text" id="title" value="${this._config.title || 'Alarm Clock'}" />
      </div>
    `;

    this.shadowRoot!.getElementById('entity')?.addEventListener('change', (e) => {
      this._config = { ...this._config, entity: (e.target as HTMLInputElement).value };
      this._fireConfigChanged();
    });

    this.shadowRoot!.getElementById('title')?.addEventListener('change', (e) => {
      this._config = { ...this._config, title: (e.target as HTMLInputElement).value };
      this._fireConfigChanged();
    });
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
customElements.define('alarm-clock-card', AlarmClockCardElement);
customElements.define('alarm-clock-card-editor', AlarmClockCardEditor);

// Register with Home Assistant
declare global {
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description: string;
      preview?: boolean;
    }>;
  }
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'alarm-clock-card',
  name: 'Alarm Clock Card',
  description: 'A card for managing calendar-based alarms',
  preview: true,
});

console.info(
  '%c ALARM-CLOCK-CARD %c 1.0.0 ',
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;'
);

