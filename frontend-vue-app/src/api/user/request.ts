/**
 * 用户模块专用请求客户端
 */
import type { RequestClientOptions } from '@/request';

import { useAppConfig } from '@/_core/hooks';
import { preferences } from '@/_core/preferences';
import {
  authenticateResponseInterceptor,
  defaultResponseInterceptor,
  errorMessageResponseInterceptor,
  RequestClient,
} from '@/request';
import { message } from 'ant-design-vue';
import { useUserAccessStore } from '../../stores/user/access';
import { useUserAuthStore } from '../../stores/user/auth';
import { refreshTokenApi } from './auth'; // 使用已有refreshTokenApi

const { apiURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

// 创建用户请求客户端实例
function createUserRequestClient(baseURL: string, options?: RequestClientOptions) {
  const client = new RequestClient({
    ...options,
    baseURL,
  });

  /**
   * 重新认证逻辑 - 用户版本
   */
  async function doReAuthenticate() {
    console.warn('用户访问令牌或刷新令牌无效或已过期。');
    const accessStore = useUserAccessStore();
    const authStore = useUserAuthStore();
    accessStore.setUserAccessToken(null);  // 清空用户token
    if (
      preferences.app.loginExpiredMode === 'modal' &&
      accessStore.isAccessChecked
    ) {
      accessStore.setLoginExpired(true);
    } else {
      // await authStore.logout();  // 用户登出操作
    }
  }

  /**
   * 刷新用户token逻辑
   */
  async function doRefreshToken() {
    const accessStore = useUserAccessStore();
    const resp = await refreshTokenApi();  // 调用用户token刷新接口
    const newToken = resp.data;
    accessStore.setUserAccessToken(newToken);
    return newToken;
  }

  function formatToken(token: null | string) {
    return token ? `Bearer ${token}` : null;
  }

  // 请求头处理
  client.addRequestInterceptor({
    fulfilled: async (config) => {
      const accessStore = useUserAccessStore();
      
      console.log('请求拦截器 - 当前accessToken:', accessStore.getUserAccessToken);
      console.log('请求URL:', config.url);
      
      if (accessStore.getUserAccessToken) {
        config.headers.Authorization = `Bearer ${accessStore.getUserAccessToken}`;
        console.log('已设置Authorization头:', config.headers.Authorization);
      } else {
        console.warn('未找到accessToken，请求将不带Authorization头');
      }
      config.headers['Accept-Language'] = preferences.app.locale;
      return config;
    },
  });

  // 处理返回的响应数据格式
  client.addResponseInterceptor(
    defaultResponseInterceptor({
      codeField: 'code',
      dataField: 'data',
      successCode: 0,
    }),
  );

  // token 过期的处理
  client.addResponseInterceptor(
    authenticateResponseInterceptor({
      client,
      doReAuthenticate,
      doRefreshToken,
      enableRefreshToken: preferences.app.enableRefreshToken,
      formatToken,
    }),
  );

  // 通用的错误处理
  client.addResponseInterceptor(
    errorMessageResponseInterceptor((msg: string, error) => {
      const responseData = error?.response?.data ?? {};
      let errorMessage = '';
      if (responseData.data?.errors && Array.isArray(responseData.data.errors)) {
        errorMessage = responseData.data.errors.join('\n');
      } else {
        errorMessage = responseData.msg ?? responseData.error ?? responseData.message ?? '';
      }
      message.error(errorMessage || msg);
    }),
  );

  return client;
}

// 用户模块请求客户端
export const userRequestClient = createUserRequestClient(apiURL, {
  responseReturn: 'data',
});

// 用户模块基础请求客户端
export const userBaseRequestClient = new RequestClient({ baseURL: apiURL });
