import { createApp, h, type App, type ComponentPublicInstance } from 'vue';
import AlarmClockCard from './AlarmClockCard.vue';
import type { HomeAssistant, CardConfig } from './types';

interface AlarmClockCardConfig extends CardConfig {
  type?: string;
  entity?: string;
  title?: string;
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
    return 3;
  }

  public static getConfigElement(): HTMLElement {
    return document.createElement('alarm-clock-card-editor');
  }

  public static getStubConfig(): AlarmClockCardConfig {
    return {
      entity: '',
      title: 'Alarm Clock',
    };
  }
}

class AlarmClockCardEditor extends HTMLElement {
  private _config: AlarmClockCardConfig = {};

  public set hass(_hass: HomeAssistant) {
    // Store hass if needed for entity picker, etc.
  }

  public setConfig(config: AlarmClockCardConfig): void {
    this._config = config;
    this._render();
  }

  private _render(): void {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    const shadowRoot = this.shadowRoot;
    if (!shadowRoot) return;

    shadowRoot.innerHTML = `
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
        <input type="text" id="entity" value="${this._config.entity ?? ''}" />
      </div>
      <div class="form-row">
        <label>Title</label>
        <input type="text" id="title" value="${this._config.title ?? 'Alarm Clock'}" />
      </div>
    `;

    const entityInput = shadowRoot.getElementById('entity');
    const titleInput = shadowRoot.getElementById('title');

    entityInput?.addEventListener('change', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._config = { ...this._config, entity: target.value };
      this._fireConfigChanged();
    });

    titleInput?.addEventListener('change', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._config = { ...this._config, title: target.value };
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

