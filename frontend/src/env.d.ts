/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

// Home Assistant types
interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
  context: {
    id: string;
    parent_id: string | null;
    user_id: string | null;
  };
}

interface HomeAssistant {
  states: Record<string, HassEntity>;
  services: Record<string, Record<string, unknown>>;
  user: {
    id: string;
    name: string;
    is_admin: boolean;
  };
  language: string;
  callService: (
    domain: string,
    service: string,
    data?: Record<string, unknown>,
    target?: { entity_id?: string | string[] }
  ) => Promise<void>;
}

interface CardConfig {
  type: string;
  entity?: string;
  title?: string;
}

