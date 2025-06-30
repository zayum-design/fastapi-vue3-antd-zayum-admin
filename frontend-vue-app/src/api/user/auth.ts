import { userBaseRequestClient, userRequestClient } from './request';
import type { UserInfo } from '@/_core/types';

export namespace UserAuthApi {
  /** 用户名密码登录参数 */
  export interface LoginParams {
    username: string;
    password: string;
    captcha: boolean;
  }

  /** 手机验证码登录参数 */
  export interface SmsLoginParams {
    phone: string;
    code: string; // 验证码(虚拟)
  }

  /** 二维码登录参数 */ 
  export interface QrLoginParams {
    qrCode: string; // 二维码内容(虚拟)
  }

  /** 注册参数 */
  export interface RegisterParams {
    username: string;
    password: string;
    phone?: string;
    email?: string;
  }

  /** 忘记密码参数 */
  export interface ForgotPasswordParams {
    username: string;
    newPassword: string;
    code: string; // 验证码(虚拟)
  }

  /** 第三方登录参数 */
  export interface SocialLoginParams {
    type: string; // 第三方类型(wechat/qq/weibo等)
    code: string; // 第三方授权码(虚拟)
  }

  /** 登录结果 */
  export interface LoginResult {
    access_token: string;
    data?: {
      user_info?: UserInfo;
    };
  }
}

/**
 * 用户名密码登录
 */
export async function loginApi(data: UserAuthApi.LoginParams) {
  return userRequestClient.post<UserAuthApi.LoginResult>('/user/auth/login', data);
}

/**
 * 手机验证码登录
 */
export async function smsLoginApi(data: UserAuthApi.SmsLoginParams) {
  return userRequestClient.post<UserAuthApi.LoginResult>('/user/auth/sms_login', data);
}

/**
 * 获取短信验证码(虚拟)
 */
export async function getSmsCodeApi(phone: string) {
  return userRequestClient.get('/user/auth/sms_code', { params: { phone } });
}

/**
 * 二维码登录 
 */
export async function qrLoginApi(data: UserAuthApi.QrLoginParams) {
  return userRequestClient.post<UserAuthApi.LoginResult>('/user/auth/qr_login', data);
}

/**
 * 获取登录二维码(虚拟)
 */
export async function getQrCodeApi() {
  return userRequestClient.get<{ qrCode: string }>('/user/auth/qr_code');
}

/**
 * 用户注册
 */
export async function registerApi(data: UserAuthApi.RegisterParams) {
  return userRequestClient.post<UserAuthApi.LoginResult>('/user/auth/register', data);
}

/**
 * 忘记密码
 */
export async function forgotPasswordApi(data: UserAuthApi.ForgotPasswordParams) {
  return userRequestClient.post('/user/auth/forgot_password', data);
}

/**
 * 第三方登录
 */
export async function socialLoginApi(data: UserAuthApi.SocialLoginParams) {
  return userRequestClient.post<UserAuthApi.LoginResult>('/user/auth/social_login', data);
}

/**
 * 获取用户信息
 */
export async function getProfileApi() {
  return userRequestClient.get<UserInfo>('/user/auth/profile');
}

/**
 * 刷新accessToken
 */
export async function refreshTokenApi() {
  return userBaseRequestClient.post<{ data: string }>('/user/auth/refresh_token', {
    withCredentials: true,
  });
}

/**
 * 退出登录
 */
export async function logoutApi() {
  return userBaseRequestClient.post('/user/auth/logout', {
    withCredentials: true,
  });
}

/**
 * 获取权限码列表
 */
export async function getAccessCodesApi() {
  return userRequestClient.get<string[]>('/user/auth/access_codes');
}
