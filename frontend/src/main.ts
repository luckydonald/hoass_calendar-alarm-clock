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

  public static getConfigElement(): AlarmClockCardEditor {
    return document.createElement('alarm-clock-card-editor') as AlarmClockCardEditor;
  }

  public static getStubConfig(): AlarmClockCardConfig {
    return {
      type: 'custom:alarm-clock-card',
      title: 'Alarm Clock',
    };
  }
}

// Schema for ha-form
const SCHEMA = [
  {
    name: 'title',
    selector: { text: {} },
  },
  {
    name: 'entity',
    selector: {
      entity: {
        domain: 'sensor',
        integration: 'calendar_alarm_clock',
      },
    },
  },
];

class AlarmClockCardEditor extends HTMLElement {
  private _config: AlarmClockCardConfig = {};
  private _hass: HomeAssistant | null = null;

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

    // Use ha-form for native HA experience
    this.innerHTML = `
      <ha-form
        .hass=${this._hass}
        .data=${this._config}
        .schema=${SCHEMA}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;

    // Since we can't use lit-html easily, fall back to manual DOM
    this._renderManual();
  }

  private _renderManual(): void {
    this.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.style.padding = '16px';

    // Title input
    const titleRow = document.createElement('div');
    titleRow.style.marginBottom = '16px';

    const titleLabel = document.createElement('label');
    titleLabel.textContent = 'Title';
    titleLabel.style.display = 'block';
    titleLabel.style.marginBottom = '4px';
    titleLabel.style.fontWeight = '500';
    titleLabel.style.color = 'var(--primary-text-color)';

    const titleInput = document.createElement('ha-textfield') as HTMLInputElement;
    titleInput.setAttribute('label', 'Card title');
    titleInput.setAttribute('value', this._config.title ?? 'Alarm Clock');
    titleInput.style.width = '100%';
    titleInput.addEventListener('input', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._updateConfig({ title: target.value });
    });

    titleRow.appendChild(titleLabel);
    titleRow.appendChild(titleInput);

    // Entity picker
    const entityRow = document.createElement('div');
    entityRow.style.marginBottom = '16px';

    const entityLabel = document.createElement('label');
    entityLabel.textContent = 'Entity (optional - for single alarm view)';
    entityLabel.style.display = 'block';
    entityLabel.style.marginBottom = '4px';
    entityLabel.style.fontWeight = '500';
    entityLabel.style.color = 'var(--primary-text-color)';

    const entityPicker = document.createElement('ha-entity-picker');
    entityPicker.setAttribute('allow-custom-entity', '');
    entityPicker.setAttribute('label', 'Entity (optional)');
    if (this._config.entity) {
      entityPicker.setAttribute('value', this._config.entity);
    }
    (entityPicker as any).hass = this._hass;
    (entityPicker as any).includeDomains = ['sensor'];
    entityPicker.style.width = '100%';
    entityPicker.addEventListener('value-changed', (e: Event) => {
      const customEvent = e as CustomEvent;
      this._updateConfig({ entity: customEvent.detail.value || '' });
    });

    entityRow.appendChild(entityLabel);
    entityRow.appendChild(entityPicker);

    // Help text
    const helpText = document.createElement('div');
    helpText.style.color = 'var(--secondary-text-color)';
    helpText.style.fontSize = '12px';
    helpText.style.marginTop = '8px';
    helpText.innerHTML = `
      <p style="margin: 0 0 8px 0;"><strong>List View (default):</strong> Leave entity empty to show all alarms.</p>
      <p style="margin: 0;"><strong>Single Alarm View:</strong> Select a specific alarm entity to show details for one alarm.</p>
    `;

    wrapper.appendChild(titleRow);
    wrapper.appendChild(entityRow);
    wrapper.appendChild(helpText);

    this.appendChild(wrapper);
  }

  private _updateConfig(update: Partial<AlarmClockCardConfig>): void {
    this._config = { ...this._config, ...update };
    this._fireConfigChanged();
  }

  private _computeLabel(schema: { name: string }): string {
    const labels: Record<string, string> = {
      title: 'Title',
      entity: 'Entity (optional, for single alarm view)',
    };
    return labels[schema.name] || schema.name;
  }

  private _valueChanged(ev: CustomEvent): void {
    this._config = ev.detail.value;
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
customElements.define('alarm-clock-card', AlarmClockCardElement);
customElements.define('alarm-clock-card-editor', AlarmClockCardEditor);

// Register with Home Assistant's custom card registry
// This makes the card appear in the card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'alarm-clock-card',
  name: 'Alarm Clock Card',
  description: 'A card for managing calendar-based alarms with snooze and dismiss',
  preview: true,
});

console.info(
  '%c ALARM-CLOCK-CARD %c 1.0.1 ',
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;'
);

