/**
 * @zh_CN 后台路由前缀
 */
export const ADMIN_ROUTE_PREFIX = import.meta.env.VITE_ADMIN_ROUTE_PREFIX || 'admin';

/**
 * @zh_CN 用户路由前缀
 */
export const USER_ROUTE_PREFIX = import.meta.env.VITE_USER_ROUTE_PREFIX || 'user';

/**
 * @zh_CN Web路由前缀
 */
export const WEB_ROUTE_PREFIX = import.meta.env.VITE_WEB_ROUTE_PREFIX || 'web';

/**
 * @zh_CN 登录页面 url 地址
 */
export const ADMIN_LOGIN_PATH = `/${ADMIN_ROUTE_PREFIX}/login`;

/**
 * @zh_CN 默认后台首页地址
 */
export const DEFAULT_ADMIN_PATH = `/${ADMIN_ROUTE_PREFIX}/dashboard/workspace`;

/**
 * @zh_CN 默认首页地址
 */
export const DEFAULT_HOME_PATH = `/${WEB_ROUTE_PREFIX}/home`;

/**
 * @zh_CN 用户登录页面 url 地址
 */
export const USER_LOGIN_PATH = `/${USER_ROUTE_PREFIX}/login`;

/**
 * @zh_CN 用户默认首页地址
 */
export const DEFAULT_USER_PATH = `/${USER_ROUTE_PREFIX}/home`;

export interface LanguageOption {
  label: string;
  value: 'en-US' | 'zh-CN';
}

/**
 * Supported languages
 */
export const SUPPORT_LANGUAGES: LanguageOption[] = [
  {
    label: '简体中文',
    value: 'zh-CN',
  },
  {
    label: 'English',
    value: 'en-US',
  },
];
