import { baseRequestClient, requestClient } from '@/api/request';
import type { UserInfo } from '@/_core/types';

export namespace AuthApi {
  /** 登录接口参数 */
  export interface LoginParams {
    password?: string;
    username?: string;
    captcha_type?: string;
    captcha?: boolean;
    captcha_id?: string | null;
    captcha_code?: string | null;
  }

  /** 登录接口返回值 */
  export interface LoginResult {
    access_token: string;
  }

  export interface RefreshTokenResult {
    data: string;
    status: number;
  }
}

/**
 * 登录
 */
export async function loginApi(data: AuthApi.LoginParams) {
  return requestClient.post<AuthApi.LoginResult>('/admin/auth/login', data);
}

/**
 * 刷新accessToken
 */
export async function refreshTokenApi() {
  return baseRequestClient.post<AuthApi.RefreshTokenResult>('/admin/auth/refresh_token', {
    withCredentials: true,
  });
}

/**
 * 退出登录
 */
export async function logoutApi() {
  return baseRequestClient.post('/admin/auth/logout', {
    withCredentials: true,
  });
}

/**
 * 获取用户权限码
 */
export async function getAccessCodesApi() {
  return requestClient.get<string[]>('/admin/auth/access_code');
}

/**
 * 获取用户信息
 */
export async function getProfileApi() {
  return requestClient.get<UserInfo>('/admin/auth/profile');
}

/**
 * 保存用户信息
 */
export async function saveProfileApi(data: any) {
    const url = '/admin/auth/profile';
    return requestClient['post'](url, data);
}
