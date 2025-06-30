import type { BasicAdminInfo } from '@/_core/typings';

/** 用户信息 */
interface UserInfo {
  avatar: string;
  created_at: string;
  email: string;
  group_id: number;
  id: number;
  login_at: string;
  login_failure: number;
  login_ip: string;
  mobile: string;
  nickname: string;
  roles: string[];
  status: string;
  token: string;
  updated_at: string;
  username: string;
}

export type { UserInfo };
