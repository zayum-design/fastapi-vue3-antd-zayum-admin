/**
 * @zh_CN 登录页面 url 地址
 */
export const ADMIN_LOGIN_PATH = '/admin/login';

/**
 * @zh_CN 默认首页地址
 */
export const DEFAULT_ADMIN_PATH = '/admin/dashboard/workspace';

export const DEFAULT_HOME_PATH = '/web/home';

/**
 * @zh_CN 用户登录页面 url 地址
 */
export const USER_LOGIN_PATH = '/user/login';

/**
 * @zh_CN 用户默认首页地址
 */
export const DEFAULT_USER_PATH = '/user/home';

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
