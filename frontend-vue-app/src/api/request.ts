/**
 * 该文件可自行根据业务逻辑进行调整
 */
import type { RequestClientOptions } from '@/_core/request';

import { useAppConfig } from '@/_core/hooks';
import { preferences } from '@/_core/preferences';
import {
  authenticateResponseInterceptor,
  defaultResponseInterceptor,
  errorMessageResponseInterceptor,
  RequestClient,
} from '@/_core/request';
import { useAdminAccessStore } from '@/stores';

import { message } from 'ant-design-vue';

import { useAuthStore } from '@/store/admin';

import { refreshTokenApi } from './admin';

const { apiURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

// 创建请求客户端实例
function createRequestClient(baseURL: string, options?: RequestClientOptions) {
  const client = new RequestClient({
    ...options,
    baseURL,
  });

  /**
   * 重新认证逻辑
   * 主要处理 token 过期或无效时的重新认证操作
   */
  async function doReAuthenticate() {
    console.warn('访问令牌或刷新令牌无效或已过期。');
    const accessStore = useAdminAccessStore();
    const authStore = useAuthStore();
    accessStore.setAccessToken(null);  // 清空 token
    if (
      preferences.app.loginExpiredMode === 'modal' &&  // 如果配置为弹窗方式处理过期
      accessStore.isAccessChecked
    ) {
      accessStore.setLoginExpired(true);  // 设置登录过期状态
    } else {
      await authStore.logout();  // 如果是自动登出方式，则执行登出操作
    }
  }

  /**
   * 刷新 token 逻辑
   * 用于刷新过期的 token，获取新的 access token
   */
  async function doRefreshToken() {
    const accessStore = useAdminAccessStore();
    const resp = await refreshTokenApi();  // 调用刷新 token 接口
    const newToken = resp.data;  // 获取新的 token
    accessStore.setAccessToken(newToken);  // 更新 token
    return newToken;
  }

  /**
   * 格式化 token
   * 将 token 格式化为 'Bearer token' 形式
   */
  function formatToken(token: null | string) {
    return token ? `Bearer ${token}` : null;
  }

  // 请求头处理
  client.addRequestInterceptor({
    fulfilled: async (config) => {
      const accessStore = useAdminAccessStore();

      // 在请求头中添加 Authorization 和 Accept-Language 字段
      config.headers.Authorization = formatToken(accessStore.adminAccessToken);
      config.headers['Accept-Language'] = preferences.app.locale;
      return config;
    },
  });

  // 处理返回的响应数据格式
  client.addResponseInterceptor(
    defaultResponseInterceptor({
      codeField: 'code',  // 响应中的字段名称，表示响应状态码
      dataField: 'data',  // 响应中的字段名称，表示响应数据
      successCode: 0,     // 成功的响应码
    }),
  );

  // token 过期的处理
  client.addResponseInterceptor(
    authenticateResponseInterceptor({
      client,
      doReAuthenticate,   // 过期时调用的重新认证函数
      doRefreshToken,     // 过期时调用的刷新 token 函数
      enableRefreshToken: preferences.app.enableRefreshToken, // 是否启用 token 刷新
      formatToken,
    }),
  );

  // 通用的错误处理
  // 如果没有进入上面的错误处理逻辑，就会进入这里
  client.addResponseInterceptor(
    errorMessageResponseInterceptor((msg: string, error) => {
      // 这里可以根据业务进行定制,你可以拿到 error 内的信息进行定制化处理，根据不同的 code 做不同的提示
      // 当前mock接口返回的错误字段是 error 或者 message
      const responseData = error?.response?.data ?? {};
      let errorMessage = '';
      if (responseData.data?.errors && Array.isArray(responseData.data.errors)) {
        errorMessage = responseData.data.errors.join('\n'); // 用换行符连接所有错误信息
      } else {
        // 回退逻辑：尝试从msg、error或message字段获取
        errorMessage = responseData.msg ?? responseData.error ?? responseData.message ?? '';
      }
      // 如果没有错误信息，则会根据状态码进行提示
      message.error(errorMessage || msg);  // 显示错误信息
    }),
  );

  return client;
}

// 创建一个请求客户端实例，返回的数据只包含 'data' 字段
export const requestClient = createRequestClient(apiURL, {
  responseReturn: 'data',
});

// 创建一个基础请求客户端实例
export const baseRequestClient = new RequestClient({ baseURL: apiURL });
