import { type App, type ComponentPublicInstance, createApp, h } from 'vue';
import AlarmClockCard from './AlarmClockCard.vue';
import type { CardConfig, HomeAssistant } from './types';
import colorName from 'color-name';

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
    };
  }
}

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
    this._renderManual();
  }

  private _renderManual(): void {
    this.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.style.padding = '16px';
    wrapper.style.display = 'flex';
    wrapper.style.flexDirection = 'column';
    wrapper.style.gap = '16px';

    // Title input
    wrapper.appendChild(this._createTextInput(
      'title',
      'Card Title',
      this._config.title ?? 'Calendar backed Alarm Clock',
    ));

    // Entity picker (for single alarm view)
    wrapper.appendChild(this._createEntityPicker());

    // Clock display select
    wrapper.appendChild(this._createSelect(
      'clock_display',
      'Clock Display',
      this._config.clock_display ?? 'analog',
      [
        { value: 'analog', label: 'Analog' },
        { value: '24h', label: 'Digital (24h)' },
        { value: '12h', label: 'Digital (12h)' },
        { value: 'none', label: 'None' },
      ],
    ));

    // Clock color settings (use color picker helper)
    wrapper.appendChild(this._createColorInput(
      'clock_bg_color',
      'Clock Background Color',
      this._config.clock_bg_color ?? 'var(--clock-day-bg)'
    ));
    wrapper.appendChild(this._createColorInput(
      'clock_hour_color',
      'Clock Hour Color',
      this._config.clock_hour_color ?? 'var(--primary-text-color)'
    ));
    wrapper.appendChild(this._createColorInput(
      'clock_minute_color',
      'Clock Minute Color',
      this._config.clock_minute_color ?? 'var(--primary-text-color)'
    ));
    wrapper.appendChild(this._createColorInput(
      'clock_second_color',
      'Clock Second Color',
      this._config.clock_second_color ?? 'var(--primary-color)'
    ));
    wrapper.appendChild(this._createColorInput(
      'clock_middle_color',
      'Clock Middle (dot/separator) Color',
      this._config.clock_middle_color ?? 'var(--primary-color)'
    ));

    // Seconds toggle
    wrapper.appendChild(this._createToggle(
      'clock_show_seconds',
      'Show Seconds on Clock',
      this._config.clock_show_seconds !== false,
    ));

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

    // Alarm list days/count input
    if (this._config.alarm_list_mode === 'count') {
      wrapper.appendChild(this._createNumberInput(
        'alarm_list_count',
        'Number of Alarms to Show',
        this._config.alarm_list_count ?? 10,
        1,
        100,
      ));
    } else {
      wrapper.appendChild(this._createNumberInput(
        'alarm_list_days',
        'Days to Show',
        this._config.alarm_list_days ?? 7,
        1,
        365,
      ));
    }

    // Section visibility toggles
    const sectionHeader = document.createElement('div');
    sectionHeader.style.fontWeight = '500';
    sectionHeader.style.marginTop = '8px';
    sectionHeader.textContent = 'Section Visibility';
    wrapper.appendChild(sectionHeader);

    wrapper.appendChild(this._createToggle(
      'show_clock',
      'Show Clock Section',
      this._config.show_clock !== false,
    ));

    wrapper.appendChild(this._createToggle(
      'show_quick_alarm',
      'Show Quick Alarm Section',
      this._config.show_quick_alarm !== false,
    ));

    wrapper.appendChild(this._createToggle(
      'show_alarm_list',
      'Show Alarm List Section',
      this._config.show_alarm_list !== false,
    ));

    // Add section mode
    wrapper.appendChild(this._createSelect(
      'show_add_section',
      'Add Alarm Section',
      this._config.show_add_section ?? 'auto',
      [
        { value: 'auto', label: 'Auto (show when Add clicked)' },
        { value: 'on', label: 'Always show' },
        { value: 'off', label: 'Never show (dialog only)' },
      ],
    ));

    // Help text
    const helpText = document.createElement('div');
    helpText.style.color = 'var(--secondary-text-color)';
    helpText.style.fontSize = '12px';
    helpText.style.marginTop = '8px';
    helpText.innerHTML = `
      <p style="margin: 0 0 8px 0;"><strong>List View (default):</strong> Leave entity empty to show all alarms.</p>
      <p style="margin: 0;"><strong>Single Alarm View:</strong> Select a specific alarm entity to show details for one alarm.</p>
    `;
    wrapper.appendChild(helpText);

    this.appendChild(wrapper);
  }

  private _createTextInput(
    name: string,
    label: string,
    value: string,
  ): HTMLDivElement {
    const row = document.createElement('div');

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.style.display = 'block';
    labelEl.style.marginBottom = '4px';
    labelEl.style.fontWeight = '500';
    labelEl.style.color = 'var(--primary-text-color)';

    const input = document.createElement('ha-textfield') as HTMLInputElement;
    input.setAttribute('label', label);
    input.setAttribute('value', value);
    input.style.width = '100%';
    input.addEventListener('input', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._updateConfig({ [name]: target.value });
    });

    row.appendChild(labelEl);
    row.appendChild(input);
    return row;
  }

  private _createNumberInput(
    name: string,
    label: string,
    value: number,
    min: number,
    max: number,
  ): HTMLDivElement {
    const row = document.createElement('div');

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.style.display = 'block';
    labelEl.style.marginBottom = '4px';
    labelEl.style.fontWeight = '500';
    labelEl.style.color = 'var(--primary-text-color)';

    const input = document.createElement('ha-textfield') as HTMLInputElement;
    input.setAttribute('type', 'number');
    input.setAttribute('label', label);
    input.setAttribute('value', String(value));
    input.setAttribute('min', String(min));
    input.setAttribute('max', String(max));
    input.style.width = '100%';
    input.addEventListener('input', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._updateConfig({ [name]: Number(target.value) });
    });

    row.appendChild(labelEl);
    row.appendChild(input);
    return row;
  }

  private _createSelect(
    name: string,
    label: string,
    value: string,
    options: Array<{ value: string; label: string; }>,
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
      const optionEl = document.createElement('ha-list-item');
      optionEl.setAttribute('value', opt.value);
      optionEl.textContent = opt.label;
      if (opt.value === value) {
        optionEl.setAttribute('selected', '');
      }
      select.appendChild(optionEl);
    });

    (select as any).value = value;

    select.addEventListener('selected', (e: Event) => {
      const target = e.target as HTMLSelectElement;
      this._updateConfig({ [name]: target.value });
    });

    row.appendChild(labelEl);
    row.appendChild(select);
    return row;
  }

  private _createToggle(
    name: string,
    label: string,
    checked: boolean,
  ): HTMLDivElement {
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.alignItems = 'center';
    row.style.justifyContent = 'space-between';

    const labelEl = document.createElement('span');
    labelEl.textContent = label;
    labelEl.style.color = 'var(--primary-text-color)';

    const toggle = document.createElement('ha-switch') as HTMLInputElement;
    if (checked) {
      toggle.setAttribute('checked', '');
    }
    toggle.addEventListener('change', (e: Event) => {
      const target = e.target as HTMLInputElement;
      this._updateConfig({ [name]: target.checked });
    });

    row.appendChild(labelEl);
    row.appendChild(toggle);
    return row;
  }

  private _createEntityPicker(): HTMLDivElement {
    const row = document.createElement('div');

    const labelEl = document.createElement('label');
    labelEl.textContent = 'Entity (optional - for single alarm view)';
    labelEl.style.display = 'block';
    labelEl.style.marginBottom = '4px';
    labelEl.style.fontWeight = '500';
    labelEl.style.color = 'var(--primary-text-color)';

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

    row.appendChild(labelEl);
    row.appendChild(entityPicker);
    return row;
  }

  private _createColorInput(
    name: string,
    label: string,
    value: string,
  ): HTMLDivElement {
    const row = document.createElement('div');

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.style.display = 'block';
    labelEl.style.marginBottom = '4px';
    labelEl.style.fontWeight = '500';
    labelEl.style.color = 'var(--primary-text-color)';

    // Container holds the textfield, dropdown/search and native color input
    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.gap = '8px';
    container.style.alignItems = 'center';

    // Text input where user can paste any CSS color string
    const textInput = document.createElement('ha-textfield') as HTMLInputElement;
    textInput.setAttribute('label', label);
    textInput.setAttribute('value', value || '');
    textInput.style.flex = '1';

    // Search box to filter the dropdown
    const searchInput = document.createElement('ha-textfield') as HTMLInputElement;
    searchInput.setAttribute('label', 'Search Colors');
    searchInput.setAttribute('value', '');
    searchInput.style.width = '180px';

    // Dropdown select showing vars + color names
    const select = document.createElement('ha-select') as HTMLSelectElement;
    select.setAttribute('label', 'Colors');
    select.style.width = '260px';

    // Native color input for color chooser
    const colorInput = document.createElement('input') as HTMLInputElement;
    colorInput.type = 'color';
    colorInput.title = 'Pick color';
    colorInput.style.width = '48px';
    colorInput.style.height = '32px';
    colorInput.style.padding = '0';
    colorInput.style.border = 'none';
    colorInput.style.background = 'transparent';

    // Build options list (vars + color names)
    const VAR_OPTIONS: Array<{ value: string; label: string; }> = [
      { value: 'var(--clock-day-bg)', label: 'var(--clock-day-bg)' },
      { value: 'var(--clock-night-bg)', label: 'var(--clock-night-bg)' },
      { value: 'var(--primary-text-color)', label: 'var(--primary-text-color)' },
      { value: 'var(--primary-color)', label: 'var(--primary-color)' },
      { value: 'var(--error-color)', label: 'var(--error-color)' },
      { value: 'var(--warning-color)', label: 'var(--warning-color)' },
    ];

    // A compact set of common CSS color names (keeps file size reasonable)
    const COLOR_NAMES = Object.keys(colorName).sort();

    const ALL_OPTIONS: Array<{ value: string; label: string; }> = [
      ...VAR_OPTIONS,
      ...COLOR_NAMES.map((n) => ({ value: n, label: n })),
    ];

    function rebuildOptions(filter = '') {
      select.innerHTML = '';
      const f = filter.trim().toLowerCase();
      ALL_OPTIONS.forEach((opt) => {
        if (f && !(opt.label.toLowerCase().includes(f))) return;
        const optionEl = document.createElement('ha-list-item');
        optionEl.setAttribute('value', opt.value);
        // Render color swatch if possible
        const swatch = `<span style="display:inline-block;width:12px;height:12px;margin-right:8px;border:1px solid rgba(0,0,0,0.15);background:${opt.value};vertical-align:middle;"></span>`;
        optionEl.innerHTML = `${swatch}${opt.label}`;
        select.appendChild(optionEl);
      });
    }

    // Try to set color input based on a CSS color string (returns hex or null)
    function colorToHex(cssColor: string): string | null {
      try {
        const el = document.createElement('div');
        el.style.color = cssColor;
        document.body.appendChild(el);
        const cs = getComputedStyle(el).color;
        document.body.removeChild(el);
        if (!cs) return null;
        // cs is like 'rgb(r, g, b)' or 'rgba(...)'
        const m = cs.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
        if (!m) return null;
        const r = parseInt(m[1], 10);
        const g = parseInt(m[2], 10);
        const b = parseInt(m[3], 10);
        const hex = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
        return hex;
      } catch {
        return null;
      }
    }

    // Initialize select options
    rebuildOptions();

    // Try to sync initial color input value
    const initialHex = colorToHex(value);
    if (initialHex) colorInput.value = initialHex;

    // Event wiring
    // text input changes
    textInput.addEventListener('input', (e: Event) => {
      const v = (e.target as HTMLInputElement).value;
      this._updateConfig({ [name]: v });
      const hex = colorToHex(v);
      if (hex) colorInput.value = hex;
    });

    // search input filters dropdown
    searchInput.addEventListener('input', (e: Event) => {
      const v = (e.target as HTMLInputElement).value;
      rebuildOptions(v);
    });

    // select choose option
    select.addEventListener('selected', (e: Event) => {
      const targ = e.target as HTMLSelectElement;
      const chosen = (targ.value as string) || '';
      // set text input and color input (if convertible)
      textInput.setAttribute('value', chosen);
      this._updateConfig({ [name]: chosen });
      const hex = colorToHex(chosen);
      if (hex) colorInput.value = hex;
    });

    // color input (native picker) change
    colorInput.addEventListener('input', (e: Event) => {
      const v = (e.target as HTMLInputElement).value;
      // write hex to text input
      textInput.setAttribute('value', v);
      this._updateConfig({ [name]: v });
    });

    // Put pieces together
    const leftGroup = document.createElement('div');
    leftGroup.style.display = 'flex';
    leftGroup.style.flexDirection = 'column';
    leftGroup.style.flex = '1';
    leftGroup.appendChild(textInput);

    const rightGroup = document.createElement('div');
    rightGroup.style.display = 'flex';
    rightGroup.style.flexDirection = 'column';
    rightGroup.style.gap = '6px';
    rightGroup.appendChild(searchInput);
    rightGroup.appendChild(select);

    container.appendChild(leftGroup);
    container.appendChild(rightGroup);
    container.appendChild(colorInput);

    row.appendChild(labelEl);
    row.appendChild(container);
    return row;
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
});

console.info(
  '%c CALENDAR-ALARM-CLOCK-CARD %c 0.0.0-dev0 ',
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;',
);
