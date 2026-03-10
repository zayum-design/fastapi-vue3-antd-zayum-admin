import type { RouteRecordStringComponent } from '@/_core/types';

import { userRequestClient } from './request';

/**
 * 获取用户所有菜单
 */
export async function getAllUserRouterApi() {
  return userRequestClient.get<RouteRecordStringComponent[]>('/user/auth/all_router');
}
