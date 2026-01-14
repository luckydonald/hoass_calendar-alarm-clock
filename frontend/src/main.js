import { createApp, h } from 'vue';
import AlarmClockCard from './AlarmClockCard.vue';

// Define the custom element
class AlarmClockCardElement extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
    this._app = null;
    this._root = null;
  }

  set hass(hass) {
    this._hass = hass;
    if (this._app && this._app._instance) {
      this._app._instance.proxy.hass = hass;
    }
  }

  setConfig(config) {
    this._config = config;
    if (this._app && this._app._instance) {
      this._app._instance.proxy.config = config;
    }
  }

  connectedCallback() {
    if (!this._root) {
      this._root = document.createElement('div');
      this.appendChild(this._root);
    }

    this._app = createApp({
      data() {
        return {
          hass: null,
          config: {},
        };
      },
      render() {
        return h(AlarmClockCard, {
          hass: this.hass,
          config: this.config,
        });
      },
    });

    this._app.mount(this._root);
    this._app._instance.proxy.hass = this._hass;
    this._app._instance.proxy.config = this._config;
  }

  disconnectedCallback() {
    if (this._app) {
      this._app.unmount();
      this._app = null;
    }
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement('alarm-clock-card-editor');
  }

  static getStubConfig() {
    return {
      entity: '',
      title: 'Alarm Clock',
    };
  }
}

// Define the editor element
class AlarmClockCardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  set hass(hass) {
    this._hass = hass;
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  _render() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    this.shadowRoot.innerHTML = `
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

    this.shadowRoot.getElementById('entity').addEventListener('change', (e) => {
      this._config = { ...this._config, entity: e.target.value };
      this._fireConfigChanged();
    });

    this.shadowRoot.getElementById('title').addEventListener('change', (e) => {
      this._config = { ...this._config, title: e.target.value };
      this._fireConfigChanged();
    });
  }

  _fireConfigChanged() {
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

