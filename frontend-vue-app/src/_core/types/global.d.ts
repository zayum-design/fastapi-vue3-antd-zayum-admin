import type { RouteMeta as IRouteMeta } from '@/_core/typings';

import 'vue-router';

declare module 'vue-router' {
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface RouteMeta extends IRouteMeta {}
}

export interface ZayumProAppConfigRaw {
  VITE_GLOB_API_URL: string;
  VITE_GLOB_URL: string;
}

export interface ApplicationConfig {
  apiURL: string;
  webURL: string;
}

declare global {
  interface Window {
    _ZAYUM_ADMIN_PRO_APP_CONF_: ZayumProAppConfigRaw;
  }
}
