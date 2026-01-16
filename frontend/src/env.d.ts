/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

// Augment HTMLElementTagNameMap for Home Assistant custom elements
declare global {
  interface HTMLElementTagNameMap {
    'ha-card': HTMLElement & {
      header?: string;
    };
    'ha-icon': HTMLElement & {
      icon: string;
    };
  }

  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description: string;
      preview?: boolean;
    }>;
  }
}

// Declare Home Assistant custom elements as Vue global components
declare module 'vue' {
  export interface GlobalComponents {
    'ha-card': HTMLElement;
    'ha-icon': HTMLElement;
  }
}

export {};
